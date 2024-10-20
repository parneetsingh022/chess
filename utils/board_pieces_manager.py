import pygame
from .pieces import Piece, PieceType, PieceColor

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

    def select_piece(self, pos):
        if pos is None:
            self.selected_piece = None
            return
        self.selected_piece = pos

    def move_piece(self, to_pos):
        
        if not self.selected_piece:
            return
        
        from_pos = self.selected_piece
        if to_pos == from_pos:
            return
        
        for i, (piece, x, y) in enumerate(self.pieces):
            if (x, y) == from_pos:
                self.pieces[i] = (piece, to_pos[0], to_pos[1])
                break
        self.selected_piece = None  # Deselect the piece after moving