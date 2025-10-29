from enum import Enum
import pygame
from utils.resource_path import resource_path

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

# Global cache for the chess pieces image to avoid repeated loading
_piece_image_cache = None

# Global cache for pre-scaled piece surfaces
_scaled_piece_cache = {}

class Piece:
    def __init__(self, screen: pygame.Surface, square_size: int, player: str, piece_type: PieceType, piece_color: PieceColor):
        global _piece_image_cache
        
        self.screen = screen
        self.square_size = square_size
        self.player = player
        self.piece_type = piece_type
        self.piece_color = piece_color

        self.piece_width = 128  # Assuming each piece is 128x128 pixels
        self.piece_height = 128
        
        # Load the image only once and cache it
        if _piece_image_cache is None:
            _piece_image_cache = pygame.image.load(resource_path("assets/chess_pieces_edited.png")).convert_alpha()
        self.image = _piece_image_cache

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
    
    def display(self, x, y, board_top_bar_height: int, absolute_coordinates: bool = False):
        """
        Display the extracted piece on the screen at the specified coordinates and draw a rectangle around it.

        Args:
            x (int): The x square from(1-8).
            y (int): The y square from(1-8).

        Returns:
            None
        """
        # Adjust the coordinates based on the player's perspective
        if not absolute_coordinates:
            if self.player == "black":
                x = 9 - x
                y = 9 - y

            x = (x - 1) * self.square_size
            y = (y - 1) * self.square_size + board_top_bar_height

        # Create a cache key based on piece type, color, and size
        cache_key = (self.piece_type.value, self.piece_color.value, self.square_size)
        
        # Check if this piece at this size is already cached
        if cache_key not in _scaled_piece_cache:
            piece = self._extract_piece()
            new_size = (self.square_size, self.square_size)
            _scaled_piece_cache[cache_key] = pygame.transform.smoothscale(piece, new_size)
        
        resized_piece = _scaled_piece_cache[cache_key]

        # Display the resized piece on the screen
        self.screen.blit(resized_piece, (x, y))