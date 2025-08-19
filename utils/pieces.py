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

class Piece:
    # Class-level caches to avoid reloading & rescaling every frame
    _sprite_sheet: pygame.Surface | None = None
    _sprite_piece_w = 128
    _sprite_piece_h = 128
    _surface_cache: dict[tuple[int, PieceType, PieceColor], pygame.Surface] = {}
    _mini_cache: dict[tuple[int, PieceType, PieceColor], pygame.Surface] = {}

    @classmethod
    def _ensure_sheet(cls):
        if cls._sprite_sheet is None:
            cls._sprite_sheet = pygame.image.load(resource_path("assets/chess_pieces_edited.png")).convert_alpha()

    @classmethod
    def get_surface(cls, size: int, piece_type: PieceType, piece_color: PieceColor) -> pygame.Surface:
        """Return a cached (size x size) surface for given piece specification."""
        cls._ensure_sheet()
        key = (size, piece_type, piece_color)
        cache = cls._surface_cache
        surf = cache.get(key)
        if surf is not None:
            return surf
        # Extract raw subsurface
        row = piece_color.value
        col = piece_type.value
        rect = pygame.Rect(col * cls._sprite_piece_w, row * cls._sprite_piece_h, cls._sprite_piece_w, cls._sprite_piece_h)
        raw = cls._sprite_sheet.subsurface(rect)  # type: ignore[arg-type]
        if size == cls._sprite_piece_w:  # unlikely but guard
            surf = raw
        else:
            # smoothscale once
            surf = pygame.transform.smoothscale(raw, (size, size))
        cache[key] = surf
        return surf

    def __init__(self, screen: pygame.Surface, square_size: int, player: str, piece_type: PieceType, piece_color: PieceColor):
        self.screen = screen
        self.square_size = square_size
        self.player = player
        self.piece_type = piece_type
        self.piece_color = piece_color
        # Pre-fetch scaled surface (cached) for main board size
        self._board_surface = self.get_surface(self.square_size, self.piece_type, self.piece_color)

    def _extract_piece(self):
        # Kept for backward compatibility; now returns cached board-sized surface
        return self._board_surface
    
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

        # Board-sized cached surface already scaled
        surf = self._board_surface
        # If square_size changed dynamically (resize), refresh
        if surf.get_width() != self.square_size:
            self._board_surface = self.get_surface(self.square_size, self.piece_type, self.piece_color)
            surf = self._board_surface
        self.screen.blit(surf, (x, y))

    @staticmethod
    def get_mini_surface(size: int, piece_type: PieceType, piece_color: PieceColor) -> pygame.Surface:
        # Convenience for external panels; uses same cache
        return Piece.get_surface(size, piece_type, piece_color)