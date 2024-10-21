import pygame
from .pieces import Piece, PieceType, PieceColor
from .movements.pawn import pawn_moves
from .movements.bishop import bishop_moves
from .movements.knight import knight_moves
from .movements.rook import rook_moves
from .movements.king import king_moves
from .movements.queen import queen_moves

def get_possible_positions(piece, color, board, x, y, king_moved):
    if piece.piece_type == PieceType.PAWN:
        return pawn_moves(board, color, x, y)
    elif piece.piece_type == PieceType.BISHOP:
        return bishop_moves(board, color, x, y)
    elif piece.piece_type == PieceType.KNIGHT:
        return knight_moves(board, color, x, y)
    elif piece.piece_type == PieceType.ROOK:
        return rook_moves(board, color, x, y)
    elif piece.piece_type == PieceType.KING:
        return king_moves(board, color, x, y, king_moved)
    elif piece.piece_type == PieceType.QUEEN:
        return queen_moves(board, color, x, y)
    return []

class BoardPiecesManager:
    def __init__(self, screen: pygame.Surface, square_size: int, player: str):
        self.screen = screen
        self.square_size = square_size
        self.player = player
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
        self.king_moved = False

    def _draw_rectangle(self, x, y):
        x = (x - 1) * self.square_size
        y = (y - 1) * self.square_size

        pygame.draw.rect(self.screen, (105, 176, 50), (x, y, self.square_size, self.square_size), 4)
        pygame.display.flip()

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
        for piece, x, y in self.pieces:
            piece.display(x, y)
        
        # Draw rectangle around the selected piece
        if self.selected_piece:
            self._draw_rectangle(self.selected_piece[0], self.selected_piece[1])

    def select_piece(self, pos):
        if pos is None:
            self.selected_piece = None
            return
        
        # Check if there is a piece at the given position
        for piece, x, y in self.pieces:
            if (x, y) == pos:
                self.selected_piece = pos
                moves = get_possible_positions(piece, piece.piece_color.name.lower(), self.layout, x, y, self.king_moved)
                self.selected_possible_moves = moves
                return
            
        self.selected_piece = None

    def move_piece(self, to_pos):
        if not self.selected_piece:
            return
        
        from_pos = self.selected_piece
        if to_pos == from_pos:
            self.selected_piece = None
            self.selected_possible_moves = []
            return
        
        # Convert coordinates to integers
        from_x, from_y = int(from_pos[0]), int(from_pos[1])
        to_x, to_y = int(to_pos[0]), int(to_pos[1])

        if (to_x, to_y) not in self.selected_possible_moves:
            self.selected_piece = None
            self.selected_possible_moves = []
            return
        
        for i, (piece, x, y) in enumerate(self.pieces):
            if (x, y) == (from_x, from_y):
                # Update the layout
                self.layout[from_y - 1][from_x - 1] = ""
                self.layout[to_y - 1][to_x - 1] = f"{piece.piece_color.name[0]}{piece.piece_type.name[0]}"
                
                # Move the piece
                self.pieces[i] = (piece, to_x, to_y)

                # Set king_moved to True if the piece is a king
                if piece.piece_type == PieceType.KING:
                    self.king_moved = True
                break
        self.selected_piece = None  # Deselect the piece after moving
        self.selected_possible_moves = []