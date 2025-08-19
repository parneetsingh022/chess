import pygame
from .pieces import Piece, PieceType, PieceColor
from .movements.pawn import pawn_moves
from .movements.bishop import bishop_moves
from .movements.knight import knight_moves
from .movements.rook import rook_moves
from .movements.king import king_moves, is_check
from .movements.queen import queen_moves
from components.turn_indicator import TurnIndicator
from utils.local_storage.storage import settings_file_manager
from states.gamestate import game_state
from components.popup import Popup
from constants.fonts import CHECK_MATETEXT_MAIN
from states.gamestate import game_state
from utils.network.lan import send_move, recv_message, send_reset, send_reset_request, send_reset_accept, send_reset_reject
from utils.sound_manager import get_sound_manager
import chess, chess.engine
import random
import os
import threading
import time




def get_possible_positions(piece, color, board, x, y, king_moved, rook1_moved, rook2_moved, en_passant_target=None):
    # Adjust positions based on player perspective
    if piece.piece_type == PieceType.PAWN:
        moves = pawn_moves(board, color, x, y, en_passant_target=en_passant_target)
    elif piece.piece_type == PieceType.BISHOP:
        moves = bishop_moves(board, color, x, y)
    elif piece.piece_type == PieceType.KNIGHT:
        moves = knight_moves(board, color, x, y)
    elif piece.piece_type == PieceType.ROOK:
        moves = rook_moves(board, color, x, y)
    elif piece.piece_type == PieceType.KING:
        moves = king_moves(board, color, x, y, king_moved, rook1_moved, rook2_moved)
    elif piece.piece_type == PieceType.QUEEN:
        moves = queen_moves(board, color, x, y)
    else:
        moves = []

    # If the king is under check, filter moves to only include those that prevent check
    valid_moves = []
    for move in moves:
        new_board = [row[:] for row in board]  # Create a copy of the board
        new_board[y-1][x-1] = ""  # Remove the piece from the original position
        piece_code = f"{color[0]}{piece.piece_type.name[0]}"
        if piece.piece_type == PieceType.KNIGHT:
            piece_code = f"{color[0]}N"
        # Handle en passant in simulation: if moving pawn to empty en_passant target, remove the adjacent pawn
        if piece.piece_type == PieceType.PAWN and en_passant_target is not None and move == en_passant_target and new_board[move[1]-1][move[0]-1] == "":
            # Remove the captured pawn which is adjacent on the from-rank
            adj_x = move[0]-1
            adj_y = y-1
            if 0 <= adj_x < 8 and 0 <= adj_y < 8:
                new_board[adj_y][adj_x] = ""
        new_board[move[1]-1][move[0]-1] = piece_code.upper()  # Place the piece in the new position
        if not is_check(new_board, "white" if color == "black" else "black")[0]:
            
            valid_moves.append(move)
            
    moves = valid_moves

    return moves

class BoardPiecesManager:
    def __init__(self, screen: pygame.Surface, square_size: int, player: str, board_top_bar_height: int):
        self.screen = screen
        self.square_size = square_size
        self.player = player
        self.board_top_bar_height = board_top_bar_height
        self.turn_indicator_height = 5
        self.turn_indicator = TurnIndicator(self.screen.get_width(), self.turn_indicator_height)
        # Stockfish engine integration (path provided by user)
        self.engine_path = r"C:\\Users\\parne\\OneDrive\\Documents\\chess2\\stockfish\\stockfish-windows-x86-64-avx2.exe"
        self.engine = None  # Lazy init when first needed
        self.engine_lock = threading.Lock()
        self.engine_thinking = False
        self._engine_thread = None
        # Suppress automatic engine replies after undo/redo until player makes a new move
        self._suppress_engine_until_player_move = False

        # Reset/consent popups
        self.reset_popup = Popup(self.screen, "Are you sure you want to reset the game?", button_type="yesno", callbacks={"yes": self.reset_popup_yes, "no": self.reset_popup_no})
        self.reset_confirm_popup = Popup(self.screen, "Opponent wants to reset. Do you agree?", button_type="yesno", callbacks={"yes": self._reset_confirm_yes, "no": self._reset_confirm_no})
        self.reset_rejected_popup = Popup(self.screen, "Opponent rejected the reset.", button_type="ok", callbacks={"ok": lambda: None})
        self.reset_waiting_popup = Popup(self.screen, "Waiting for opponent approval...", button_type="none")

        # Resign popups
        self.resign_popup = Popup(self.screen, "Are you sure you want to resign?", button_type="yesno", callbacks={"yes": self._resign_yes, "no": lambda: None})
        self.opponent_resigned_popup = Popup(self.screen, "Opponent resigned. You win!", button_type="ok", callbacks={"ok": lambda: None})

        # Drag-and-drop state for pieces
        self.dragging = False
        self._drag_piece_index = None
        self._drag_pos = None  # screen pixel coords
        # Multiplayer: track opponent's last move (from_pos, to_pos) in 1-based coords
        self.opponent_last_move = None
        # Bot rating & timing (rating-based adaptive bot). Will be set on Start based on user selection.
        self.bot_rating = 400  # fallback baseline until user picks
        self.bot_move_delay = 0.6  # target total delay (thinking + post delay) lightweight
        self._engine_rating_config_applied = None  # track last rating applied to engine options

        # Move history for undo/redo
        self.move_history = []
        self.history_index = -1
        # Flag to cancel an in-progress engine think when user undoes/redoes
        self._cancel_think = False

        # Initialize game state (after history fields defined so reset can use them)
        self.reset()
        self.event = None


    def add_event(self, event):
        self.event = event  

    def reset_popup_yes(self):
        # In multiplayer, request consent first; in single player, reset immediately
        if game_state.multiplayer and game_state.net_socket is not None:
            send_reset_request(game_state.net_socket)
            # Show waiting indicator until peer responds
            self.reset_waiting_popup.show()
            # Keep popup visible state blocked until response comes
            return
        game_state.in_game = False
        self.reset()
        game_state.check_position = None

    def reset_popup_no(self):
        pass

    def resign(self):
        # Ask for confirmation to resign
        self.resign_popup.show()

    def _resign_yes(self):
        # Local player resigns: end game and notify opponent if applicable
        game_state.in_game = False
        game_state.check_position = None
        try:
            if game_state.multiplayer and game_state.net_socket is not None:
                # Send a simple resign message over existing socket (JSON line)
                game_state.net_socket.sendall(("{\"type\": \"resign\"}\n").encode("utf-8"))
        except Exception:
            pass
        # Reset board to initial state
        self.reset()

    def reset(self, show_p=False, flip=False):
        if show_p:
            self.reset_popup.show()
            return

        self.layout = [
            ["BR", "BN", "BB", "BQ", "BK", "BB", "BN", "BR"],
            ["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP"],
            ["WR", "WN", "WB", "WQ", "WK", "WB", "WN", "WR"]
        ] if not flip else self.layout

        self.pieces = self._initialize_pieces()
        self.selected_piece = None
        self.selected_possible_moves = []

        if flip:
            return

        self.turn = "white"

        self.white_king_moved = False
        self.black_king_moved = False

        self.white_rook1_moved = False
        self.white_rook2_moved = False
        self.black_rook1_moved = False
        self.black_rook2_moved = False

        self.is_under_check = False
        self.is_check_mate = False

        self.last_moved_pos = None
        self.opponent_last_move = None

        # En passant: target square available for en passant capture on the immediate next move
        self.en_passant_target = None
        # If human chose black in single-player, let engine (white) start immediately
        if not flip:
            try:
                # Engine should only start after user has explicitly started the game
                if game_state.in_game and not game_state.multiplayer and self.player == "black":
                    self._start_engine_think()
            except Exception:
                pass
        # Initialize history (only on full reset, not flip)
        if not flip:
            self.move_history.clear()
            self.history_index = -1
            self._push_history_snapshot()

    # Don't reset global game state here; menu/start flow controls it.

    def _draw_rectangle(self, x, y, color=(105, 176, 50)):
        if self.player == "black":
            x = 9 - x
            y = 9 - y

        x = (x - 1) * self.square_size
        y = (y - 1) * self.square_size + self.board_top_bar_height

        pygame.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size), 4)

    def _draw_filled_square(self, x, y, color=(255, 215, 0), alpha=90):
        """Draw a translucent filled square at board coords (1-8,1-8)."""
        bx, by = x, y
        if self.player == "black":
            bx = 9 - bx
            by = 9 - by
        px = (bx - 1) * self.square_size
        py = (by - 1) * self.square_size + self.board_top_bar_height
        surf = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        r, g, b = color
        surf.fill((r, g, b, alpha))
        self.screen.blit(surf, (px, py))

    def _no_move_left(self):
        if not self.is_under_check: return
        for piece in self.pieces:
            if piece[0].piece_color.name.lower() == self.turn:
                ep_target = self.en_passant_target if piece[0].piece_type == PieceType.PAWN else None
                moves = get_possible_positions(piece[0], piece[0].piece_color.name.lower(), self.layout, piece[1], piece[2], False, False, False, ep_target)
                if moves: return False

        return True

    def _draw_circle(self, x, y):
        if self.player == "black":
            x = 9 - x
            y = 9 - y
        # Calculate the center of the square
        x_center = (x - 1) * self.square_size + self.square_size // 2
        y_center = (y - 1) * self.square_size + self.square_size // 2 + self.board_top_bar_height

        # Create a higher resolution surface (4 times the original size)
        high_res_size = self.square_size * 4
        high_res_surface = pygame.Surface((high_res_size, high_res_size), pygame.SRCALPHA)

        # Draw the circle on the high resolution surface
        pygame.draw.circle(high_res_surface, (105, 176, 50), (high_res_size // 2, high_res_size // 2), high_res_size // 6)

        # Scale the high resolution surface down to the original size
        scaled_surface = pygame.transform.smoothscale(high_res_surface, (self.square_size, self.square_size))

        # Blit the scaled surface onto the main screen
        self.screen.blit(scaled_surface, (x_center - self.square_size // 2, y_center - self.square_size // 2))

    def _draw_checkmate_popup(self):
        start_x = 0
        start_y = self.board_top_bar_height
        
        font = CHECK_MATETEXT_MAIN
        text = font.render("Checkmate!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        
        # Define the background color and rectangle size
        background_color = (0, 0, 0, 180)  # Black background with transparency (alpha = 180)
        
        # Create a new surface with an alpha channel that covers the entire screen
        background_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        
        # Draw the background rectangle on the new surface
        pygame.draw.rect(background_surface, background_color, background_surface.get_rect())
        
        # Blit the background surface onto the main screen
        self.screen.blit(background_surface, (start_x, start_y))
        
        # Draw the text on top of the background
        self.screen.blit(text, text_rect)

    def _pixel_to_square(self, x: int, y: int) -> tuple[int, int] | None:
        """Convert screen pixel coordinates to 1-based board square coords, or None if outside board."""
        # Adjust for top bar
        y_adj = y - self.board_top_bar_height
        if y_adj < 0:
            return None
        bx = x // self.square_size + 1
        by = y_adj // self.square_size + 1
        if not (1 <= bx <= 8 and 1 <= by <= 8):
            return None
        if self.player == "black":
            bx = 9 - bx
            by = 9 - by
        return int(bx), int(by)

    def _initialize_pieces(self):
        pieces = []
        for y, row in enumerate(self.layout):
            for x, piece_code in enumerate(row):
                if piece_code:
                    piece_color = PieceColor.WHITE if piece_code[0] == 'W' else PieceColor.BLACK
                    piece_type = {
                        'P': PieceType.PAWN,
                        'N': PieceType.KNIGHT,
                        'B': PieceType.BISHOP,
                        'R': PieceType.ROOK,
                        'Q': PieceType.QUEEN,
                        'K': PieceType.KING
                    }[piece_code[1]]
                    piece = Piece(self.screen, self.square_size, self.player, piece_type, piece_color)
                    pieces.append((piece, x + 1, y + 1))
        return pieces

    def show_promotion_options(self, pos, color):
        """Display promotion options for the pawn."""
        x, y = pos
        options = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]
        option_size = self.square_size // 1.5
        option_rects = []

        # Calculate the total width and height of the promotion options
        total_width = len(options) * option_size
        total_height = option_size

        # Calculate the initial starting position
        if self.player == "black":
            start_x = (8 - x) * self.square_size + (self.square_size - total_width) // 2
            start_y = (8 - y) * self.square_size + 2 * self.board_top_bar_height
        else:
            start_x = (x - 1) * self.square_size + (self.square_size - total_width) // 2
            start_y = (y - 1) * self.square_size + 2 * self.board_top_bar_height

        # Ensure the box doesn't go outside the window horizontally
        if start_x < 0:
            start_x = 0  # Align to the left edge
        elif start_x + total_width > self.screen.get_width():
            start_x = self.screen.get_width() - total_width  # Align to the right edge

        # Ensure the box doesn't go outside the window vertically
        if start_y < 0:
            start_y = 0  # Align to the top edge
        elif start_y + total_height > self.screen.get_height():
            start_y = self.screen.get_height() - total_height  # Align to the bottom edge

        # Draw the outer border
        outer_rect = pygame.Rect(start_x, start_y, total_width, total_height)
        pygame.draw.rect(self.screen, (200, 200, 200), outer_rect)  # Light grey color
        pygame.draw.rect(self.screen, (0, 0, 0), outer_rect, 2)  # Black border with width 2

        for i, option in enumerate(options):
            rect_x = start_x + i * option_size
            rect_y = start_y
            rect = pygame.Rect(rect_x, rect_y, option_size, option_size)
            option_rects.append((rect, option))

            # Display the piece
            piece = Piece(self.screen, option_size, self.player, option, color)
            piece.display(rect_x, rect_y, 0, absolute_coordinates=True)

        pygame.display.flip()
        return option_rects


    
    def handle_promotion_selection(self, pos, color):
        """Handle the selection of the promotion piece."""
        option_rects = self.show_promotion_options(pos, color)
        selected_piece_type = None

        while not selected_piece_type:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for rect, piece_type in option_rects:
                        if rect.collidepoint(mouse_pos):
                            selected_piece_type = piece_type
                            break

        return selected_piece_type
    
    def display(self):
        if self.last_moved_pos is not None:
            self._draw_rectangle(*self.last_moved_pos, color=(128, 128, 128))
        # In multiplayer, highlight opponent's last move (from and to squares)
        if game_state.multiplayer and self.opponent_last_move:
            f, t = self.opponent_last_move
            # Use gold-ish overlay; differentiate from general selection
            self._draw_filled_square(f[0], f[1], color=(255, 223, 0), alpha=70)
            self._draw_filled_square(t[0], t[1], color=(255, 223, 0), alpha=70)
        # Trigger engine first move only after game start (removed default_player orientation setting logic)
        try:
            if (game_state.in_game and not game_state.multiplayer and
                self.player == "black" and self.turn == "white" and not self.engine_thinking):
                self._start_engine_think()
        except Exception:
            pass
        
        if self.is_check_mate or self._no_move_left():
            self.is_check_mate = True
            self.selected_piece = None
        
        
        if game_state.start_new:
            self.reset()
            game_state.start_new = False

        if settings_file_manager.get_setting("turn_indicator"):
            if self.player == "white":
                if self.turn == "white":
                    self.turn_indicator.set_position(0, self.screen.get_height() - self.turn_indicator_height)
                else:
                    self.turn_indicator.set_position(0, self.board_top_bar_height)
            else:  # self.chess_board_manager.player == "black"
                if self.turn == "black":
                    self.turn_indicator.set_position(0, self.screen.get_height() - self.turn_indicator_height)
                else:
                    self.turn_indicator.set_position(0, self.board_top_bar_height)
            self.turn_indicator.display(self.screen)

        # Draw pieces; if dragging, draw dragged piece last at cursor
        dragged_piece = None
        dragged_idx = self._drag_piece_index if self.dragging else None
        for idx, (piece, x, y) in enumerate(self.pieces):
            if self.dragging and dragged_idx is not None and idx == dragged_idx:
                dragged_piece = piece
                continue
            piece.display(x, y, self.board_top_bar_height)
        # Draw dragged piece following cursor
        if self.dragging and dragged_piece is not None and self._drag_pos is not None:
            px, py = self._drag_pos
            # Center piece on cursor
            draw_x = px - self.square_size // 2
            draw_y = py - self.square_size // 2
            dragged_piece.display(draw_x, draw_y, 0, absolute_coordinates=True)
        
        # Draw rectangle around the selected piece
        if self.selected_piece:
            self._draw_rectangle(self.selected_piece[0], self.selected_piece[1])
        
        # Draw circles for all possible moves
        if settings_file_manager.get_setting("movement_indicators"):
            for move in self.selected_possible_moves:
                self._draw_circle(move[0], move[1])


        if self.is_check_mate:
            self._draw_checkmate_popup()

        # Draw popups (render only; event handling below)
        self.reset_popup.draw()
        self.reset_confirm_popup.draw()
        self.reset_rejected_popup.draw()
        self.reset_waiting_popup.draw()
        self.resign_popup.draw()
        self.opponent_resigned_popup.draw()

        # Do not flip here; the screen will be updated once per frame by the parent screen

        # Handle the event
        if self.event:
            # Handle any visible popup events first
            if self.reset_popup.handle_event(self.event):
                return
            if self.reset_confirm_popup.handle_event(self.event):
                return
            if self.reset_rejected_popup.handle_event(self.event):
                return
            if self.resign_popup.handle_event(self.event):
                return
            if self.opponent_resigned_popup.handle_event(self.event):
                return

            # Drag-and-click interactions for pieces (left mouse)
            if self.event.type == pygame.MOUSEBUTTONDOWN and self.event.button == 1:
                pos = self._pixel_to_square(*self.event.pos)
                if pos is not None:
                    if self.selected_piece:
                        # If clicking on the already selected piece, start dragging
                        if pos == self.selected_piece and settings_file_manager.get_setting("drag_drop"):
                            idx = self._get_piece_index_at_pos(self.selected_piece)
                            if idx is not None:
                                self.dragging = True
                                self._drag_piece_index = idx
                                self._drag_pos = self.event.pos
                                # Change cursor to hand while dragging
                                try:
                                    pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
                                except Exception:
                                    try:
                                        pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND))
                                    except Exception:
                                        pass
                        # Else: keep selection; BoardPage will handle click-to-move on mouse up
                    else:
                        # No selection yet: attempt to select piece at pos
                        self.select_piece(pos)
                        if self.selected_piece is not None and settings_file_manager.get_setting("drag_drop"):
                            # Start dragging immediately when selecting a piece on mousedown
                            idx = self._get_piece_index_at_pos(self.selected_piece)
                            if idx is not None:
                                self.dragging = True
                                self._drag_piece_index = idx
                                self._drag_pos = self.event.pos
                                # Change cursor to hand while dragging
                                try:
                                    pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
                                except Exception:
                                    try:
                                        pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND))
                                    except Exception:
                                        pass
            elif self.event.type == pygame.MOUSEMOTION and self.dragging and pygame.mouse.get_pressed()[0]:
                # Update drag position while holding left button
                self._drag_pos = self.event.pos
            elif self.event.type == pygame.MOUSEBUTTONUP and self.event.button == 1:
                # Stop dragging on release; BoardPage will trigger the move using current cursor square
                if self.dragging:
                    self.dragging = False
                    self._drag_piece_index = None
                    self._drag_pos = None
                    # Restore default arrow cursor
                    try:
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    except Exception:
                        try:
                            pygame.mouse.set_cursor(pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW))
                        except Exception:
                            pass

        # Poll for incoming network moves if in multiplayer
        if game_state.multiplayer and game_state.net_socket is not None:
            msg = recv_message(game_state.net_socket)
            if msg:
                if msg.get("type") == "move":
                    f = tuple(msg.get("from"))
                    t = tuple(msg.get("to"))
                    # Apply the move directly
                    self.select_piece(f, force=True)
                    self.move_piece(t)
                    # Track opponent's last move
                    self.opponent_last_move = (f, t)
                elif msg.get("type") == "reset":
                    # Legacy immediate reset (keep for compatibility)
                    game_state.in_game = False
                    game_state.check_position = None
                    self.reset()
                elif msg.get("type") == "reset_request":
                    # Show confirm popup to this player
                    self.reset_confirm_popup.show()
                elif msg.get("type") == "reset_accept":
                    # Peer accepted; perform reset locally
                    # Hide any waiting indicator
                    self.reset_waiting_popup.hide()
                    game_state.in_game = False
                    game_state.check_position = None
                    self.reset()
                elif msg.get("type") == "reset_reject":
                    # Peer rejected; inform the requester
                    self.reset_waiting_popup.hide()
                    self.reset_rejected_popup.show()
                elif msg.get("type") == "resign":
                    # Opponent resigned; show info popup
                    self.opponent_resigned_popup.show()

    def _reset_confirm_yes(self):
        # Send acceptance and reset locally
        if game_state.multiplayer and game_state.net_socket is not None:
            send_reset_accept(game_state.net_socket)
        game_state.in_game = False
        game_state.check_position = None
        self.reset()

    def _reset_confirm_no(self):
        # Send rejection only
        if game_state.multiplayer and game_state.net_socket is not None:
            send_reset_reject(game_state.net_socket)

    def select_piece(self, pos, force: bool = False):
        # Block any selection before game has started (unless force is explicitly used internally)
        if not game_state.in_game and not force:
            self.selected_piece = None
            self.selected_possible_moves = []
            return
        if game_state.pop_up_on: 
            self.selected_piece = None
            return

        if pos is None:
            self.selected_piece = None
            self.selected_possible_moves = []
            return
        
        # Check if there is a piece at the given position
        for piece, x, y in self.pieces:
            if (x, y) == pos:
                self.selected_piece = pos
                if not force:
                    # Enforce turn
                    if piece.piece_color.name.lower() != self.turn:
                        self.selected_piece = None
                        self.selected_possible_moves = []
                        return
                    # In multiplayer, also restrict to the local player's color
                    if game_state.multiplayer and game_state.my_color and piece.piece_color.name.lower() != game_state.my_color:
                        self.selected_piece = None
                        self.selected_possible_moves = []
                        return
                if piece.piece_type == PieceType.KING:
                    king_moved = self.white_king_moved if piece.piece_color == PieceColor.WHITE else self.black_king_moved
                    rook1_moved = self.white_rook1_moved if piece.piece_color == PieceColor.WHITE else self.black_rook1_moved
                    rook2_moved = self.white_rook2_moved if piece.piece_color == PieceColor.WHITE else self.black_rook2_moved
                    moves = get_possible_positions(piece, piece.piece_color.name.lower(), self.layout, x, y, king_moved, rook1_moved, rook2_moved, self.en_passant_target)
                else:
                    moves = get_possible_positions(piece, piece.piece_color.name.lower(), self.layout, x, y, False, False, False, self.en_passant_target if piece.piece_type == PieceType.PAWN else None)
                self.selected_possible_moves = moves
                return
            
        self.selected_piece = None
        self.selected_possible_moves = []

    def remove_piece(self, pos):
        for i, (_, x, y) in enumerate(self.pieces):
            if (x, y) == pos:
                # Remove the piece from both the pieces list and the layout
                self.layout[y - 1][x - 1] = ""  # Convert to 0-based for layout
                self.pieces.pop(i)
                break

    def move_piece(self, to_pos):
        # Prevent any movement before Start is pressed
        if not game_state.in_game:
            return
        if game_state.pop_up_on:
            return
        if not self.selected_piece:
            return

        from_pos = self.selected_piece
        if to_pos == from_pos:
            return  # No movement

        from_x, from_y = int(from_pos[0]) - 1, int(from_pos[1]) - 1
        to_x, to_y = int(to_pos[0]) - 1, int(to_pos[1]) - 1

        if not (0 <= to_x < 8 and 0 <= to_y < 8):
            self.selected_piece = None
            self.selected_possible_moves = []
            return

        if (to_x + 1, to_y + 1) not in self.selected_possible_moves:
            self.selected_piece = None
            self.selected_possible_moves = []
            if self.layout[to_y][to_x] and self.layout[to_y][to_x][0] == self.layout[from_y][from_x][0]:
                self.select_piece(to_pos)
            return

        game_state.in_game = True
        captured_piece_index = None
        promotion_suffix = ""
        moved = False

        for i, (piece, x, y) in enumerate(self.pieces):
            if (x - 1, y - 1) != (from_x, from_y):
                continue

            prev_en_passant = self.en_passant_target
            self.en_passant_target = None

            if self.layout[to_y][to_x] != "":
                captured_piece_index = self._get_piece_index_at_pos((to_x + 1, to_y + 1))
            else:
                if piece.piece_type == PieceType.PAWN and prev_en_passant == (to_x + 1, to_y + 1) and abs(to_x - from_x) == 1:
                    cap_index = self._get_piece_index_at_pos((to_x + 1, from_y + 1))
                    if cap_index is not None:
                        self.layout[from_y][to_x] = ""
                        captured_piece_index = cap_index

            # Update layout
            self.layout[from_y][from_x] = ""
            pname = f"{piece.piece_color.name[0]}{piece.piece_type.name[0]}"
            if piece.piece_type == PieceType.KNIGHT:
                pname = f"{piece.piece_color.name[0]}N"
            self.layout[to_y][to_x] = pname
            self.pieces[i] = (piece, to_x + 1, to_y + 1)

            # Castling
            if piece.piece_type == PieceType.KING:
                if piece.piece_color == PieceColor.WHITE:
                    self.white_king_moved = True
                else:
                    self.black_king_moved = True
                if abs(to_x - from_x) == 2:
                    rook_from_x, rook_to_x = (7, to_x - 1) if to_x > from_x else (0, to_x + 1)
                    rook_y = from_y
                    r_index = self._get_piece_index_at_pos((rook_from_x + 1, rook_y + 1))
                    if r_index is not None:
                        rook_piece, _, _ = self.pieces[r_index]
                        self.layout[rook_y][rook_from_x] = ""
                        self.layout[rook_y][rook_to_x] = f"{rook_piece.piece_color.name[0]}{rook_piece.piece_type.name[0]}"
                        self.pieces[r_index] = (rook_piece, rook_to_x + 1, rook_y + 1)

            # Rook movement flags
            if piece.piece_type == PieceType.ROOK:
                if piece.piece_color == PieceColor.WHITE:
                    if from_x == 0 and from_y == 7:
                        self.white_rook1_moved = True
                    elif from_x == 7 and from_y == 7:
                        self.white_rook2_moved = True
                else:
                    if from_x == 0 and from_y == 0:
                        self.black_rook1_moved = True
                    elif from_x == 7 and from_y == 0:
                        self.black_rook2_moved = True

            # Pawn promotion & en passant target
            if piece.piece_type == PieceType.PAWN:
                prefix = "B" if piece.piece_color == PieceColor.BLACK else "W"
                if (to_y + 1) in (8, 1):
                    selected_piece_type = self.handle_promotion_selection((to_x, to_y), piece.piece_color)
                    postfix = selected_piece_type.name[0] if selected_piece_type != PieceType.KNIGHT else "N"
                    self.layout[to_y][to_x] = f"{prefix}{postfix}"
                    self.pieces[i] = (
                        Piece(self.screen, self.square_size, self.player, selected_piece_type, piece.piece_color),
                        to_x + 1,
                        to_y + 1,
                    )
                    promotion_suffix = postfix.lower()
                if abs(to_y - from_y) == 2:
                    direction = -1 if piece.piece_color == PieceColor.WHITE else 1
                    self.en_passant_target = (from_x + 1, from_y + 1 + direction)

            self.is_under_check, king_pos_c = is_check(self.layout, self.turn)
            if self.player == "black" and king_pos_c:
                king_pos_c = (9 - king_pos_c[0], 9 - king_pos_c[1])
            game_state.check_position = king_pos_c if self.is_under_check else None

            sm = get_sound_manager()
            if captured_piece_index is not None:
                sm.play_capture()
            else:
                sm.play_move()

            self.turn = "white" if self.turn == "black" else "black"
            self.last_moved_pos = (to_x + 1, to_y + 1)
            moved = True
            break

        if captured_piece_index is not None:
            self.pieces.pop(captured_piece_index)

        if game_state.multiplayer and game_state.net_socket is not None and from_pos is not None and moved:
            try:
                send_move(game_state.net_socket, from_pos, to_pos)
            except Exception:
                pass

        if moved:
            try:
                sm = get_sound_manager()
                if game_state.check_position is not None:
                    sm.play_check()
            except Exception:
                pass

        if moved and not game_state.multiplayer:
            try:
                uci_move = f"{chr(ord('a') + from_x)}{8 - from_y}{chr(ord('a') + to_x)}{8 - to_y}{promotion_suffix}"
                print(uci_move, flush=True)
                # Record history after player's move
                self._push_history_snapshot()
                # Allow engine to think now (player initiated new move)
                self._suppress_engine_until_player_move = False
                self._start_engine_think()
            except Exception:
                pass

        self.selected_piece = None
        self.selected_possible_moves = []

    def _get_piece_index_at_pos(self, pos):
        """Helper function to get the index of the piece at the given position (1-based)."""
        for i, (_, x, y) in enumerate(self.pieces):
            if (x, y) == pos:
                return i
        return None

    # ---------------- UCI move application -----------------
    def apply_uci_move(self, uci_move: str):
        """Apply a UCI move (e.g. e2e4, g7g8q) to the internal board state and update game flags.
        Assumes the move is legal in the current position (minimal validation).
        """
        try:
            if not uci_move or len(uci_move) < 4:
                return
            from_file = uci_move[0]
            from_rank = int(uci_move[1])
            to_file = uci_move[2]
            to_rank = int(uci_move[3])
            promotion = uci_move[4] if len(uci_move) > 4 else None

            from_x = ord(from_file) - ord('a')
            from_y = 8 - from_rank
            to_x = ord(to_file) - ord('a')
            to_y = 8 - to_rank

            if not (0 <= from_x < 8 and 0 <= from_y < 8 and 0 <= to_x < 8 and 0 <= to_y < 8):
                return

            piece_code = self.layout[from_y][from_x]
            if not piece_code:
                return

            piece_index = self._get_piece_index_at_pos((from_x + 1, from_y + 1))
            if piece_index is None:
                return

            piece_obj, _, _ = self.pieces[piece_index]

            captured_piece_index = None
            prev_en_passant = self.en_passant_target
            self.en_passant_target = None

            target_code = self.layout[to_y][to_x]
            # Detect en passant capture (pawn moves diagonally to empty square which matches previous en passant target)
            if piece_obj.piece_type == PieceType.PAWN and target_code == "" and from_x != to_x and prev_en_passant == (to_x + 1, to_y + 1):
                # The captured pawn is on the from rank at the to file
                cap_index = self._get_piece_index_at_pos((to_x + 1, from_y + 1))
                if cap_index is not None:
                    self.layout[from_y][to_x] = ""  # remove the pawn behind
                    captured_piece_index = cap_index
            elif target_code != "":
                captured_piece_index = self._get_piece_index_at_pos((to_x + 1, to_y + 1))

            # Move piece on layout
            self.layout[from_y][from_x] = ""
            self.layout[to_y][to_x] = piece_code
            self.pieces[piece_index] = (piece_obj, to_x + 1, to_y + 1)

            # Castling (king moves two squares)
            if piece_obj.piece_type == PieceType.KING and abs(to_x - from_x) == 2:
                if piece_obj.piece_color == PieceColor.WHITE:
                    self.white_king_moved = True
                else:
                    self.black_king_moved = True
                rook_from_x, rook_to_x = (7, to_x - 1) if to_x > from_x else (0, to_x + 1)
                rook_y = from_y
                r_index = self._get_piece_index_at_pos((rook_from_x + 1, rook_y + 1))
                if r_index is not None:
                    rook_piece, _, _ = self.pieces[r_index]
                    self.layout[rook_y][rook_from_x] = ""
                    self.layout[rook_y][rook_to_x] = f"{rook_piece.piece_color.name[0]}{rook_piece.piece_type.name[0] if rook_piece.piece_type != PieceType.KNIGHT else 'N'}"
                    self.pieces[r_index] = (rook_piece, rook_to_x + 1, rook_y + 1)
            else:
                # Update king/rook moved flags when they move normally
                if piece_obj.piece_type == PieceType.KING:
                    if piece_obj.piece_color == PieceColor.WHITE:
                        self.white_king_moved = True
                    else:
                        self.black_king_moved = True
                elif piece_obj.piece_type == PieceType.ROOK:
                    if piece_obj.piece_color == PieceColor.WHITE:
                        if from_x == 0 and from_y == 7:
                            self.white_rook1_moved = True
                        elif from_x == 7 and from_y == 7:
                            self.white_rook2_moved = True
                    else:
                        if from_x == 0 and from_y == 0:
                            self.black_rook1_moved = True
                        elif from_x == 7 and from_y == 0:
                            self.black_rook2_moved = True

            # Pawn specific: promotion & new en passant target
            if piece_obj.piece_type == PieceType.PAWN:
                # Two-square advance creates en passant target
                if abs(to_y - from_y) == 2:
                    direction = -1 if piece_obj.piece_color == PieceColor.WHITE else 1
                    self.en_passant_target = (from_x + 1, from_y + 1 + direction)
                # Promotion
                if promotion:
                    promo_map = {
                        'q': PieceType.QUEEN,
                        'r': PieceType.ROOK,
                        'b': PieceType.BISHOP,
                        'n': PieceType.KNIGHT
                    }
                    ptype = promo_map.get(promotion.lower())
                    if ptype:
                        prefix = 'W' if piece_obj.piece_color == PieceColor.WHITE else 'B'
                        postfix = ptype.name[0] if ptype != PieceType.KNIGHT else 'N'
                        self.layout[to_y][to_x] = f"{prefix}{postfix}"
                        # Replace piece object
                        new_piece = Piece(self.screen, self.square_size, self.player, ptype, piece_obj.piece_color)
                        self.pieces[piece_index] = (new_piece, to_x + 1, to_y + 1)

            # Remove captured piece from list
            if captured_piece_index is not None:
                try:
                    self.pieces.pop(captured_piece_index)
                except Exception:
                    pass

            # Update check state
            self.is_under_check, king_pos_c = is_check(self.layout, self.turn)
            if self.player == "black" and king_pos_c:
                king_pos_c = (9 - king_pos_c[0], 9 - king_pos_c[1])
            game_state.check_position = king_pos_c if self.is_under_check else None

            # Sounds
            try:
                sm = get_sound_manager()
                if captured_piece_index is not None:
                    sm.play_capture()
                else:
                    sm.play_move()
                if game_state.check_position is not None:
                    sm.play_check()
            except Exception:
                pass

            # Switch turn & record
            self.turn = "white" if self.turn == "black" else "black"
            self.last_moved_pos = (to_x + 1, to_y + 1)
            # After engine (or opponent) move snapshot history (single-player only or multiplayer for local record)
            try:
                self._push_history_snapshot()
                # Engine just moved; keep suppression False so future player move can trigger engine
                self._suppress_engine_until_player_move = False
            except Exception:
                pass

        except Exception:
            pass

    # ---------------- Stockfish helpers -----------------
    def _ensure_engine(self):
        if self.engine is None:
            try:
                if os.path.exists(self.engine_path):
                    self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            except Exception:
                self.engine = None

    def _build_fen(self):
        """Construct a (approximate) FEN string from current internal state for engine query."""
        piece_letter_map = {"P": "p", "R": "r", "N": "n", "B": "b", "Q": "q", "K": "k"}
        rows = []
        for y in range(8):  # y=0 is rank 8
            fen_row = ""
            empty = 0
            for x in range(8):
                code = self.layout[y][x]
                if not code:
                    empty += 1
                else:
                    if empty:
                        fen_row += str(empty)
                        empty = 0
                    color = code[0]
                    p = piece_letter_map.get(code[1], "?")
                    if color == "W":
                        p = p.upper()
                    fen_row += p
            if empty:
                fen_row += str(empty)
            rows.append(fen_row)
        board_part = "/".join(rows)

        active = 'w' if self.turn == 'white' else 'b'

        rights = ''
        # White castling rights
        try:
            if (not self.white_king_moved and not self.white_rook2_moved and
                self.layout[7][4] == 'WK' and self.layout[7][7].startswith('WR')):
                rights += 'K'
            if (not self.white_king_moved and not self.white_rook1_moved and
                self.layout[7][4] == 'WK' and self.layout[7][0].startswith('WR')):
                rights += 'Q'
            # Black castling rights
            if (not self.black_king_moved and not self.black_rook2_moved and
                self.layout[0][4] == 'BK' and self.layout[0][7].startswith('BR')):
                rights += 'k'
            if (not self.black_king_moved and not self.black_rook1_moved and
                self.layout[0][4] == 'BK' and self.layout[0][0].startswith('BR')):
                rights += 'q'
        except Exception:
            pass
        if rights == '':
            rights = '-'

        # En passant target
        if self.en_passant_target:
            ex, ey_top = self.en_passant_target  # 1-based with top rank =1
            file_c = chr(ord('a') + ex - 1)
            rank_c = str(9 - ey_top)  # convert to chess rank
            ep = f"{file_c}{rank_c}"
        else:
            ep = '-'

        # Halfmove clock & fullmove number (approximate: reset halfmove each move, fullmove floor)
        halfmove = 0
        fullmove = 1
        return f"{board_part} {active} {rights} {ep} {halfmove} {fullmove}"

    def _print_engine_best_move(self):
        # Synchronous computation (protected by lock); prefer using _start_engine_think
        if game_state.multiplayer or self.engine_thinking:
            return
        with self.engine_lock:
            self._ensure_engine()
            if self.engine is None:
                return
            try:
                fen = self._build_fen()
                board = chess.Board(fen)
                move, _ = self._choose_bot_move(board)
                if move:
                    print(f"engine:{move.uci()}", flush=True)
            except Exception:
                pass

    def _start_engine_think(self):
        """Spawn a background thread to compute and print engine reply after the move is visually settled."""
        if self.engine_thinking or game_state.multiplayer:
            return
        # Honor suppression (e.g., after undo/redo) so engine waits for user's next manual move
        if self._suppress_engine_until_player_move:
            return
        # Mark thinking and start thread
        self.engine_thinking = True
        self._cancel_think = False

        def _worker():
            start_time = time.time()
            time.sleep(0.05)  # allow render of player's move
            try:
                with self.engine_lock:
                    self._ensure_engine()
                    if self.engine is None:
                        return
                    board = chess.Board(self._build_fen())
                    move, _think = self._choose_bot_move(board)
                    if move and not self._cancel_think:
                        uci = move.uci()
                        print(f"engine:{uci}", flush=True)
                        elapsed = time.time() - start_time
                        remaining = self.bot_move_delay - elapsed
                        if remaining > 0:
                            slept = 0.0
                            # Slice sleep to allow prompt cancellation
                            while slept < remaining and not self._cancel_think:
                                dt = min(0.02, remaining - slept)
                                time.sleep(dt)
                                slept += dt
                        if not self._cancel_think:
                            self.apply_uci_move(uci)
            except Exception:
                pass
            finally:
                self.engine_thinking = False

        t = threading.Thread(target=_worker, daemon=True)
        self._engine_thread = t
        t.start()

    # ---------------- Rating-based bot helpers -----------------
    def set_bot_rating(self, rating: int):
        """Set target bot rating (approximate)."""
        try:
            r = int(rating)
        except Exception:
            r = 300
        self.bot_rating = max(300, min(r, 3000))
    # Debug print removed
        # Invalidate previously applied engine rating so new one will be applied
        self._engine_rating_config_applied = None
        # If engine already running, apply new strength immediately so next move reflects it
        try:
            with self.engine_lock:
                if self.engine is not None:
                    self._configure_engine_strength()
        except Exception:
            pass

    def _configure_engine_strength(self):
        """Configure Stockfish built-in Elo limiting where possible (floor ~800-1000 depending on build).
        For very low requested ratings we still set the minimum and inject blunders separately.
        """
        if self.engine is None:
            return
        target = self.bot_rating
        # Stockfish typical supported range (approx) 1320-3190; we'll clamp.
        min_supported = 1320
        max_supported = 3190
        effective = max(min_supported, min(target, max_supported))
        if self._engine_rating_config_applied == effective:
            return
        try:
            self.engine.configure({
                "UCI_LimitStrength": True,
                "UCI_Elo": effective
            })
            self._engine_rating_config_applied = effective
            # Debug print removed
        except Exception:
            pass

    def _choose_bot_move(self, board: chess.Board):
        """Return (move, think_time_used) for current bot rating.
        Heuristic mapping rating -> think time, blunder chance, inaccuracy mode.
        """
        rating = self.bot_rating
    # Debug start print removed
        # Map rating to think time (seconds)
        think_time = (
            0.01 if rating <= 500 else
            0.02 if rating <= 700 else
            0.04 if rating <= 900 else
            0.07 if rating <= 1100 else
            0.12 if rating <= 1400 else
            0.2 if rating <= 1700 else
            0.35 if rating <= 2000 else
            0.5 if rating <= 2400 else
            0.7 if rating <= 2700 else
            1.0
        )
        # Total target delay scales lightly with rating (faster reply lower rating)
        self.bot_move_delay = min(1.2, 0.4 + think_time * 1.2)

        # Blunder chance for very low ratings (<= 1200). Drops linearly to 0 at 1200.
        blunder_chance = 0.0
        if rating < 1200:
            blunder_chance = min(0.6, (1200 - rating) / 1200 * 0.6)

        # Inaccuracy (choose among top N) chance for sub 1600
        inaccuracy_chance = 0.0
        if rating < 1600:
            inaccuracy_chance = 0.15 + (1600 - rating) / 1600 * 0.25  # up to 0.4

        start = time.time()
        move = None
        try:
            self._configure_engine_strength()
            if self.engine is None:
                return None, 0.0

            legal_moves = list(board.legal_moves)
            if not legal_moves:
                return None, 0.0

            # Decide if forcing blunder: choose random legal move (avoid obviously losing king moves by naive filter)
            if random.random() < blunder_chance:
                move = random.choice(legal_moves)
                return move, time.time() - start

            # Determine number of candidate moves to sample if inaccuracy
            use_multipv = 1
            if random.random() < inaccuracy_chance:
                # More candidates for lower rating
                use_multipv = 3 if rating < 1000 else 2
            # Analyse with MultiPV when needed; fallback to play for speed when only 1
            if use_multipv == 1:
                result = self.engine.play(board, chess.engine.Limit(time=think_time))
                move = result.move if result else None
            else:
                infos = self.engine.analyse(board, chess.engine.Limit(time=think_time), multipv=use_multipv)
                # infos is list of dicts, each has 'pv' principal variation
                candidates = []
                for info in infos:
                    pv = info.get('pv')
                    if pv:
                        candidates.append(pv[0])
                if not candidates:
                    result = self.engine.play(board, chess.engine.Limit(time=think_time/2))
                    move = result.move if result else None
                else:
                    # Weighted random: earlier PV higher weight
                    weights = [1.0 / (i+1) for i in range(len(candidates))]
                    total = sum(weights)
                    r = random.random() * total
                    upto = 0
                    for w, m in zip(weights, candidates):
                        if upto + w >= r:
                            move = m
                            break
                        upto += w
                    if move is None:
                        move = candidates[0]
        except Exception:
            move = None
    # Debug end print removed
        return move, time.time() - start

    # ---------------- Undo / Redo helpers -----------------
    def _snapshot_state(self) -> dict:
        """Capture current board state for undo/redo."""
        return {
            'layout': [row[:] for row in self.layout],
            'turn': self.turn,
            'white_king_moved': self.white_king_moved,
            'black_king_moved': self.black_king_moved,
            'white_rook1_moved': self.white_rook1_moved,
            'white_rook2_moved': self.white_rook2_moved,
            'black_rook1_moved': self.black_rook1_moved,
            'black_rook2_moved': self.black_rook2_moved,
            'en_passant_target': self.en_passant_target,
            'last_moved_pos': self.last_moved_pos,
            'is_check_mate': self.is_check_mate,
        }

    def _restore_state(self, snap: dict):
        self.layout = [row[:] for row in snap['layout']]
        self.pieces = self._initialize_pieces()
        self.turn = snap['turn']
        self.white_king_moved = snap['white_king_moved']
        self.black_king_moved = snap['black_king_moved']
        self.white_rook1_moved = snap['white_rook1_moved']
        self.white_rook2_moved = snap['white_rook2_moved']
        self.black_rook1_moved = snap['black_rook1_moved']
        self.black_rook2_moved = snap['black_rook2_moved']
        self.en_passant_target = snap['en_passant_target']
        self.last_moved_pos = snap['last_moved_pos']
        self.is_check_mate = snap['is_check_mate']
        # Re-evaluate check position
        try:
            self.is_under_check, king_pos_c = is_check(self.layout, self.turn)
            if self.player == "black" and king_pos_c:
                king_pos_c = (9 - king_pos_c[0], 9 - king_pos_c[1])
            game_state.check_position = king_pos_c if self.is_under_check else None
        except Exception:
            pass
        self.selected_piece = None
        self.selected_possible_moves = []

    def _push_history_snapshot(self):
        # Truncate forward history if we branched
        if self.history_index < len(self.move_history) - 1:
            self.move_history = self.move_history[:self.history_index + 1]
        self.move_history.append(self._snapshot_state())
        self.history_index = len(self.move_history) - 1

    def undo_move(self):
        """Undo last full turn (your move plus opponent/engine reply) when possible.
        If the opponent reply hasn't happened yet (engine turn), only your last move is undone.
        """
        if self.history_index <= 0:
            return
        if self.engine_thinking:
            self._cancel_think = True
            try:
                if self._engine_thread and self._engine_thread.is_alive():
                    self._engine_thread.join(timeout=0.05)
            except Exception:
                pass
        # Determine human player's color string
        player_color = self.player  # 'white' or 'black'
        # Step back one ply
        steps = 0
        while steps < 2 and self.history_index > 0:
            self.history_index -= 1
            self._restore_state(self.move_history[self.history_index])
            steps += 1
            # Stop if after undo it's player's turn (full turn undone)
            if self.turn == player_color:
                break
        # Suppress automatic engine move until player acts
        self._suppress_engine_until_player_move = True
        # Play move sound to give feedback
        try:
            get_sound_manager().play_move()
        except Exception:
            pass

    def redo_move(self):
        """Redo next full turn (your move plus engine reply) when both plies exist.
        If only your move exists ahead (engine reply not yet in history), redo just that ply.
        """
        if self.history_index >= len(self.move_history) - 1:
            return
        if self.engine_thinking:
            self._cancel_think = True
            try:
                if self._engine_thread and self._engine_thread.is_alive():
                    self._engine_thread.join(timeout=0.05)
            except Exception:
                pass
        player_color = self.player
        steps = 0
        while steps < 2 and self.history_index < len(self.move_history) - 1:
            self.history_index += 1
            self._restore_state(self.move_history[self.history_index])
            steps += 1
            if self.turn != player_color:  # engine to move means pair complete
                break
        # Keep suppression so engine does not auto-fire after redo placing position at engine's move
        if self.turn != player_color:
            self._suppress_engine_until_player_move = True
        # Play move sound for feedback
        try:
            get_sound_manager().play_move()
        except Exception:
            pass