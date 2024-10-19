from enum import Enum
from .board_pieces_manager import BoardPiecesManager

class PieceType(Enum):
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5

class PieceColor(Enum):
    BLACK = 0
    WHITE = 1


class Piece:
    def __init__(self, board_piece_manager: BoardPiecesManager, piece_type: PieceType, piece_color: PieceColor):
        self.board_piece_manager = board_piece_manager
        self.piece_type = piece_type
        self.piece_color = piece_color
        self.x = 0
        self.y = 0

    def set_position(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def display(self) -> None:
        self.board_piece_manager.display_piece(
            self.x, 
            self.y,
            self.piece_color.value ,
            self.piece_type.value 
            
        )