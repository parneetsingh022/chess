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


def get_possible_positions(piece, color, board, x, y, king_moved, rook1_moved, rook2_moved):
    # Adjust positions based on player perspective
    if piece.piece_type == PieceType.PAWN:
        moves = pawn_moves(board, color, x, y)
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
        self.reset_popup = Popup(screen, "Are you sure you want to reset the game?", button_type="yesno", callbacks={"yes": self.reset_popup_yes, "no": self.reset_popup_no})
        self.reset()

        self.event = None

        

    def add_event(self, event):
        self.event = event  

    def reset_popup_yes(self):
        game_state.in_game = False
        self.reset()

    def reset_popup_no(self):
        pass

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

        if flip: return

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

        game_state.reset()

    def _draw_rectangle(self, x, y, color=(105, 176, 50)):
        if self.player == "black":
            x = 9 - x
            y = 9 - y

        x = (x - 1) * self.square_size
        y = (y - 1) * self.square_size + self.board_top_bar_height

        pygame.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size), 4)

    def _no_move_left(self):
        if not self.is_under_check: return
        for piece in self.pieces:
            if piece[0].piece_color.name.lower() == self.turn:
                moves = get_possible_positions(piece[0], piece[0].piece_color.name.lower(), self.layout, piece[1], piece[2], False, False, False)
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
        settings_default_player = settings_file_manager.get_setting("default_player")

        if self.player != settings_default_player and settings_default_player is not None:
            settings_default_player = settings_default_player.lower()
            self.player = settings_default_player
            self.reset(flip=True)
            if game_state.check_position:
                king_pos_c = (9 - game_state.check_position[0], 9 - game_state.check_position[1])
            else:
                king_pos_c = None
            game_state.check_position = king_pos_c
        
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

        for piece, x, y in self.pieces:
            piece.display(x, y, self.board_top_bar_height)
        
        # Draw rectangle around the selected piece
        if self.selected_piece:
            self._draw_rectangle(self.selected_piece[0], self.selected_piece[1])
        
        # Draw circles for all possible moves
        if settings_file_manager.get_setting("movement_indicators"):
            for move in self.selected_possible_moves:
                self._draw_circle(move[0], move[1])


        if self.is_check_mate: self._draw_checkmate_popup()
        self.reset_popup.draw()
        
        # Update the display once after all drawing operations
        pygame.display.flip()

        # Handle the event
        if self.event:
            if self.reset_popup.handle_event(self.event):
                # If the popup handled the event, skip further processing
                return

    def select_piece(self, pos):
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
                if piece.piece_color.name.lower() != self.turn:
                    self.selected_piece = None
                    self.selected_possible_moves = []
                    return
                if piece.piece_type == PieceType.KING:
                    king_moved = self.white_king_moved if piece.piece_color == PieceColor.WHITE else self.black_king_moved
                    rook1_moved = self.white_rook1_moved if piece.piece_color == PieceColor.WHITE else self.black_rook1_moved
                    rook2_moved = self.white_rook2_moved if piece.piece_color == PieceColor.WHITE else self.black_rook2_moved
                    moves = get_possible_positions(piece, piece.piece_color.name.lower(), self.layout, x, y, king_moved, rook1_moved, rook2_moved)
                else:
                    moves = get_possible_positions(piece, piece.piece_color.name.lower(), self.layout, x, y, False, False, False)
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
        
        if game_state.pop_up_on: return
        if not self.selected_piece:
            return

        from_pos = self.selected_piece
        if to_pos == from_pos:
            self.selected_piece = None
            self.selected_possible_moves = []
            return

        # Convert 1-based to 0-based coordinates for layout access
        from_x, from_y = int(from_pos[0]) - 1, int(from_pos[1]) - 1
        to_x, to_y = int(to_pos[0]) - 1, int(to_pos[1]) - 1

        # Check if to_pos is within the bounds of the board
        if not (0 <= to_x < len(self.layout[0]) and 0 <= to_y < len(self.layout)):
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
        captured_piece_index = None  # Track index of captured piece for removal

        for i, (piece, x, y) in enumerate(self.pieces):
            if (x - 1, y - 1) == (from_x, from_y):
                # Check if there is an opponent piece at the destination
                if self.layout[to_y][to_x] != "":
                    captured_piece_index = self._get_piece_index_at_pos((to_x + 1, to_y + 1))  # Capture piece index

                # Update the layout for the moved piece
                self.layout[from_y][from_x] = ""  # Clear the old position
                pname = f"{piece.piece_color.name[0]}{piece.piece_type.name[0]}"
                if piece.piece_type == PieceType.KNIGHT:
                    pname = f"{piece.piece_color.name[0]}N"
                self.layout[to_y][to_x] = pname

                # Move the piece in self.pieces
                self.pieces[i] = (piece, to_x + 1, to_y + 1)  # Update to new position

                # Set king_moved to True if the piece is a king
                if piece.piece_type == PieceType.KING:
                    if piece.piece_color == PieceColor.WHITE:
                        self.white_king_moved = True
                    else:
                        self.black_king_moved = True

                    # Check for castling move
                    if abs(to_x - from_x) == 2:
                        if to_x > from_x:
                            # Kingside castling
                            rook_from_x = 7
                            rook_to_x = to_x - 1
                        else:
                            # Queenside castling
                            rook_from_x = 0
                            rook_to_x = to_x + 1

                        rook_y = from_y
                        rook_piece_index = self._get_piece_index_at_pos((rook_from_x + 1, rook_y + 1))
                        if rook_piece_index is not None:
                            rook_piece, _, _ = self.pieces[rook_piece_index]
                            self.layout[rook_y][rook_from_x] = ""  # Clear the old rook position
                            self.layout[rook_y][rook_to_x] = f"{rook_piece.piece_color.name[0]}{rook_piece.piece_type.name[0]}"
                            self.pieces[rook_piece_index] = (rook_piece, rook_to_x + 1, rook_y + 1)  # Update rook position

                # Set rook_moved to True if the piece is a rook
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
                

                if piece.piece_type == PieceType.PAWN:
                    prefix = "B" if piece.piece_color == PieceColor.BLACK else "W"
                    
                    if ((to_y + 1) == 8 or (to_y + 1) == 1):
                        selected_piece_type = self.handle_promotion_selection((to_x, to_y), piece.piece_color)
                        postfix = selected_piece_type.name[0] if selected_piece_type != PieceType.KNIGHT else "N"
                        self.layout[to_y][to_x] = f"{prefix}{postfix}"
                        self.pieces[i] = (
                            Piece(self.screen, self.square_size, self.player, selected_piece_type, piece.piece_color), 
                            to_x + 1, 
                            to_y + 1
                        )

                self.is_under_check, king_pos_c = is_check(self.layout, self.turn)
                if self.player == "black":
                    king_pos_c = (9 - king_pos_c[0], 9 - king_pos_c[1])
                

                if self.is_under_check:
                    game_state.check_position = king_pos_c
                else:
                    game_state.check_position = None

                self.turn = "white" if self.turn == "black" else "black" 
                self.last_moved_pos = (to_x+1,to_y+1)
                break

        # Remove the captured piece after the loop (to avoid list modification issues during iteration)
        if captured_piece_index is not None:
            self.pieces.pop(captured_piece_index)

        self.selected_piece = None
        self.selected_possible_moves = []

    def _get_piece_index_at_pos(self, pos):
        """Helper function to get the index of the piece at the given position (1-based)."""
        for i, (_, x, y) in enumerate(self.pieces):
            if (x, y) == pos:
                return i
        return None