import pygame
from typing import Tuple, Set, Optional


class HighlightManager:
    def __init__(self, chess_board_manager):
        self._cbm = chess_board_manager
        self._highlights: Set[Tuple[int, int]] = set()  # squares are 1-based (x,y)

    def toggle_highlight(self, square: Optional[Tuple[int, int]]):
        if not square:
            return
        if square in self._highlights:
            self._highlights.remove(square)
        else:
            self._highlights.add(square)

    def clear_highlights(self):
        self._highlights.clear()

    def draw_highlights(self, screen: pygame.Surface):
        if not self._highlights:
            return
        # Draw semi-transparent full-square overlay on each highlighted square
        for sq in self._highlights:
            self._draw_fill_on_square(screen, sq)

    def _square_rect(self, square: Tuple[int, int]) -> pygame.Rect:
        x1b, y1b = square
        if self._cbm.player == "white":
            sx = (x1b - 1) * self._cbm._square_size
            sy = self._cbm.board_top_bar_height + (y1b - 1) * self._cbm._square_size
        else:
            sx = (8 - x1b) * self._cbm._square_size
            sy = self._cbm.board_top_bar_height + (8 - y1b) * self._cbm._square_size
        return pygame.Rect(sx, sy, self._cbm._square_size, self._cbm._square_size)

    def _draw_fill_on_square(self, screen: pygame.Surface, square: Tuple[int, int]):
        rect = self._square_rect(square)

        # Create an alpha surface to draw a translucent full-square highlight
        fill_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Colors: semi-transparent orange fill with a slightly stronger border
        fill_color = (255, 165, 0, 90)
        border_color = (255, 69, 0, 150)

        # Fill the entire square
        pygame.draw.rect(fill_surf, fill_color, pygame.Rect(0, 0, rect.width, rect.height))

        # Optional border for clarity
        border_w = max(2, rect.width // 24)
        pygame.draw.rect(fill_surf, border_color, pygame.Rect(0, 0, rect.width, rect.height), border_w)

        # Blit on screen at board coordinates
        screen.blit(fill_surf, (rect.x, rect.y))
