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
        # Draw semi-transparent ring on each highlighted square
        for sq in self._highlights:
            self._draw_ring_on_square(screen, sq)

    def _square_rect(self, square: Tuple[int, int]) -> pygame.Rect:
        x1b, y1b = square
        if self._cbm.player == "white":
            sx = (x1b - 1) * self._cbm._square_size
            sy = self._cbm.board_top_bar_height + (y1b - 1) * self._cbm._square_size
        else:
            sx = (8 - x1b) * self._cbm._square_size
            sy = self._cbm.board_top_bar_height + (8 - y1b) * self._cbm._square_size
        return pygame.Rect(sx, sy, self._cbm._square_size, self._cbm._square_size)

    def _draw_ring_on_square(self, screen: pygame.Surface, square: Tuple[int, int]):
        rect = self._square_rect(square)

        # Create an alpha surface to draw a translucent ring
        ring_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Ring parameters
        margin = max(2, int(rect.width * 0.08))
        outer_color = (255, 69, 0, 130)  # match arrow orange, semi-transparent
        center = (rect.width // 2, rect.height // 2)
        radius = min(rect.width, rect.height) // 2 - margin
        thickness = max(4, int(rect.width * 0.12))

        # Draw outer circle (ring)
        pygame.draw.circle(ring_surf, outer_color, center, radius, thickness)

        # Optional subtle inner fill to improve visibility on dark squares
        inner_radius = max(0, radius - thickness // 2)
        fill_alpha = 40
        if inner_radius > 0:
            pygame.draw.circle(ring_surf, (255, 69, 0, fill_alpha), center, inner_radius)

        screen.blit(ring_surf, (rect.x, rect.y))
