import pygame
from .pieces import Piece, PieceType, PieceColor
from .movements.pawn import pawn_moves
from .movements.bishop import bishop_moves
from .movements.knight import knight_moves
from .movements.rook import rook_moves
from .movements.king import king_moves
from .movements.queen import queen_moves
from components.turn_indicator import TurnIndicator
from utils.local_storage.storage import settings_file_manager
from states.gamestate import game_state


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
    return moves

class BoardPiecesManager:
    def __init__(self, screen: pygame.Surface, square_size: int, player: str, board_top_bar_height: int):
        self.screen = screen
        self.square_size = square_size
        self.player = player
        self.board_top_bar_height = board_top_bar_height
        self.turn_indicator_height = 5
        self.turn_indicator = TurnIndicator(self.screen.get_width(), self.turn_indicator_height)
        #self._reset()

    def _reset(self):
        self.layout = [
            ["BR", "BN", "BB", "BQ", "BK", "BB", "BN", "BR"],
            ["BP", "BP", "BP", "BP", "BP", "BP", "BP", "BP"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["WP", "WP", "WP", "WP", "WP", "WP", "WP", "WP"],
            ["WR", "WN", "WB", "WQ", "WK", "WB", "WN", "WR"]
        ]

        self.pieces = self._initialize_pieces()
        self.selected_piece = None
        self.selected_possible_moves = []
        self.turn = "white"

        self.white_king_moved = False
        self.black_king_moved = False

        self.white_rook1_moved = False
        self.white_rook2_moved = False
        self.black_rook1_moved = False
        self.black_rook2_moved = False


    def _draw_rectangle(self, x, y):
        if self.player == "black":
            x = 9 - x
            y = 9 - y

        x = (x - 1) * self.square_size
        y = (y - 1) * self.square_size + self.board_top_bar_height

        

        pygame.draw.rect(self.screen, (105, 176, 50), (x, y, self.square_size, self.square_size), 4)

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

    def display(self):
        if game_state.start_new:
            self._reset()
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
            piece.display(x, y,self.board_top_bar_height)
        
        # Draw rectangle around the selected piece
        if self.selected_piece:
            self._draw_rectangle(self.selected_piece[0], self.selected_piece[1])
        
        # Draw circles for all possible moves
        
        if settings_file_manager.get_setting("movement_indicators"):
            for move in self.selected_possible_moves:
                self._draw_circle(move[0], move[1])
        
        # Update the display once after all drawing operations
        pygame.display.flip()

    def select_piece(self, pos):
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
        game_state.in_game = True
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

        captured_piece_index = None  # Track index of captured piece for removal

        for i, (piece, x, y) in enumerate(self.pieces):
            if (x - 1, y - 1) == (from_x, from_y):
                # Check if there is an opponent piece at the destination
                if self.layout[to_y][to_x] != "":
                    captured_piece_index = self._get_piece_index_at_pos((to_x + 1, to_y + 1))  # Capture piece index

                # Update the layout for the moved piece
                self.layout[from_y][from_x] = ""  # Clear the old position
                self.layout[to_y][to_x] = f"{piece.piece_color.name[0]}{piece.piece_type.name[0]}"

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

                self.turn = "white" if self.turn == "black" else "black"

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