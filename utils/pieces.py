from enum import Enum
import pygame

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
    def __init__(self, screen: pygame.Surface, square_size: int, player: str, piece_type: PieceType, piece_color: PieceColor):
        self.screen = screen
        self.square_size = square_size
        self.player = player
        self.piece_type = piece_type
        self.piece_color = piece_color

        self.piece_width = 128  # Assuming each piece is 128x128 pixels
        self.piece_height = 128
        self.image = pygame.image.load("assets/chess_pieces_edited.png").convert_alpha()

    def _extract_piece(self):
        """
        Extract a piece based on its row and column in the grid.

        Args:
            row (int): The row of the piece in the grid.
            col (int): The column of the piece in the grid.

        Returns:
            pygame.Surface: The surface containing the extracted piece.
        """
        row = self.piece_color.value
        col = self.piece_type.value

        rect = pygame.Rect(col * self.piece_width, row * self.piece_height, self.piece_width, self.piece_height)
        return self.image.subsurface(rect)
    
    def display(self, x, y, board_top_bar_height: int):
        """
        Display the extracted piece on the screen at the specified coordinates and draw a rectangle around it.

        Args:
            x (int): The x square from(1-8).
            y (int): The y square from(1-8).

        Returns:
            None
        """
        # Adjust the coordinates based on the player's perspective
        if self.player == "black":
            x = 9 - x
            y = 9 - y

        x = (x - 1) * self.square_size
        y = (y - 1) * self.square_size + board_top_bar_height

        piece = self._extract_piece()

        # Calculate the new size for the piece
        new_size = (self.square_size, self.square_size)

        # Resize the piece using smoothscale for better quality
        resized_piece = pygame.transform.smoothscale(piece, new_size)

        # Display the resized piece on the screen
        self.screen.blit(resized_piece, (x, y))