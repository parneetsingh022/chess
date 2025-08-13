import pygame
import pygame.gfxdraw as gfxdraw
import math
from typing import Tuple, Optional
from enum import Enum


class ArrowType(Enum):
    STRAIGHT = "straight"
    DIAGONAL = "diagonal"
    KNIGHT = "knight"


class Arrow:
    def __init__(self, start_square: Tuple[int, int], end_square: Tuple[int, int], arrow_type: ArrowType):
        self.start_square = start_square
        self.end_square = end_square
        self.arrow_type = arrow_type
        # Semi-transparent orange-red with larger default thickness
        self.color = (255, 69, 0, 160)
        self.thickness = 8


class ArrowManager:
    def __init__(self, chess_board_manager):
        self.chess_board_manager = chess_board_manager
        self.arrows = []
        self.drawing_arrow = False
        self.arrow_start_square: Optional[Tuple[int, int]] = None
        # Hover tracking (board squares) to avoid pixel jitter
        self.current_hover_square: Optional[Tuple[int, int]] = None
        # Debounce candidate to avoid boundary oscillation
        self._candidate_square: Optional[Tuple[int, int]] = None
        self._candidate_since_ms: Optional[int] = None
        self._debounce_ms = 30  # ms to remain in square before switching

    def start_drawing_arrow(self, square_pos: Tuple[int, int]):
        if square_pos is not None and 1 <= square_pos[0] <= 8 and 1 <= square_pos[1] <= 8:
            self.drawing_arrow = True
            self.arrow_start_square = square_pos

    def update_hover_square(self, square_pos: Optional[Tuple[int, int]]):
        if not self.drawing_arrow:
            return
        if square_pos and 1 <= square_pos[0] <= 8 and 1 <= square_pos[1] <= 8:
            if square_pos != self.current_hover_square:
                now = pygame.time.get_ticks()
                if self._candidate_square != square_pos:
                    self._candidate_square = square_pos
                    self._candidate_since_ms = now

    def tick(self, now_ms: Optional[int] = None):
        if not self.drawing_arrow:
            return
        if now_ms is None:
            now_ms = pygame.time.get_ticks()
        if self._candidate_square is not None and self._candidate_since_ms is not None:
            if now_ms - self._candidate_since_ms >= self._debounce_ms:
                self.current_hover_square = self._candidate_square
                self._candidate_square = None
                self._candidate_since_ms = None

    def finish_drawing_arrow(self, end_square_pos: Tuple[int, int]):
        if (self.drawing_arrow and self.arrow_start_square and end_square_pos and
            1 <= end_square_pos[0] <= 8 and 1 <= end_square_pos[1] <= 8 and
            end_square_pos != self.arrow_start_square):

            arrow_type = self._determine_arrow_type(self.arrow_start_square, end_square_pos)
            if arrow_type:
                new_arrow = Arrow(self.arrow_start_square, end_square_pos, arrow_type)
                # Deduplicate same start->end
                self.arrows = [a for a in self.arrows
                               if not (a.start_square == new_arrow.start_square and a.end_square == new_arrow.end_square)]
                self.arrows.append(new_arrow)

        # Reset drawing state
        self.drawing_arrow = False
        self.arrow_start_square = None
        self.current_hover_square = None
        self._candidate_square = None
        self._candidate_since_ms = None

    def cancel_drawing(self):
        self.drawing_arrow = False
        self.arrow_start_square = None
        self.current_hover_square = None
        self._candidate_square = None
        self._candidate_since_ms = None

    def clear_arrows(self):
        self.arrows.clear()

    def _determine_arrow_type(self, start_square: Tuple[int, int], end_square: Tuple[int, int]) -> Optional[ArrowType]:
        if start_square == end_square:
            return None
        dx = abs(end_square[0] - start_square[0])
        dy = abs(end_square[1] - start_square[1])
        if (dx == 2 and dy == 1) or (dx == 1 and dy == 2):
            return ArrowType.KNIGHT
        elif dx == 0 or dy == 0:
            return ArrowType.STRAIGHT
        elif dx == dy:
            return ArrowType.DIAGONAL
        return None

    def _square_to_pixel(self, square: Tuple[int, int]) -> Tuple[int, int]:
        square_size = self.chess_board_manager._square_size
        top = self.chess_board_manager.board_top_bar_height
        bx, by = square
        if self.chess_board_manager.player == "white":
            px = (bx - 1) * square_size + square_size // 2
            py = top + (by - 1) * square_size + square_size // 2
        else:
            px = (8 - bx) * square_size + square_size // 2
            py = top + (8 - by) * square_size + square_size // 2
        return (int(px), int(py))

    def _draw_arrow_line(self, surface: pygame.Surface, start_pos: Tuple[int, int],
                         end_pos: Tuple[int, int], color: Tuple[int, int, int] | Tuple[int, int, int, int], thickness: int):
        sx, sy = int(start_pos[0]), int(start_pos[1])
        ex, ey = int(end_pos[0]), int(end_pos[1])

        dx = ex - sx
        dy = ey - sy
        if dx == 0 and dy == 0:
            return

        angle = math.atan2(dy, dx)
        length = math.hypot(dx, dy)
        head_length = int(max(10, min(20, length * 0.25)))
        head_angle = math.pi / 6

        # Compute base of arrowhead
        base_x_f = ex - head_length * math.cos(angle)
        base_y_f = ey - head_length * math.sin(angle)

        # Overlap shaft slightly into the head to remove any gap
        overlap = max(1, thickness // 2)
        shaft_end_x = int(round(base_x_f + overlap * math.cos(angle)))
        shaft_end_y = int(round(base_y_f + overlap * math.sin(angle)))

        # Draw shaft and smooth start cap (filled + AA circle caps)
        pygame.draw.line(surface, color, (sx, sy), (shaft_end_x, shaft_end_y), thickness)
        cap_radius = max(1, thickness // 2)
        gfxdraw.filled_circle(surface, sx, sy, cap_radius, color)
        gfxdraw.aacircle(surface, sx, sy, cap_radius, color)

        # Arrowhead triangle points
        head_x1 = int(round(ex - head_length * math.cos(angle - head_angle)))
        head_y1 = int(round(ey - head_length * math.sin(angle - head_angle)))
        head_x2 = int(round(ex - head_length * math.cos(angle + head_angle)))
        head_y2 = int(round(ey - head_length * math.sin(angle + head_angle)))

        points = [(ex, ey), (head_x1, head_y1), (head_x2, head_y2)]
        gfxdraw.filled_polygon(surface, points, color)
        gfxdraw.aapolygon(surface, points, color)

    def _draw_knight_arrow(self, surface: pygame.Surface, start_pos: Tuple[int, int],
                           end_pos: Tuple[int, int], color: Tuple[int, int, int] | Tuple[int, int, int, int], thickness: int):
        sx, sy = int(start_pos[0]), int(start_pos[1])
        ex, ey = int(end_pos[0]), int(end_pos[1])
        dx = ex - sx
        dy = ey - sy

        # L-shape: keep the corner at integer grid to minimize gaps
        if abs(dx) > abs(dy):
            intermediate = (ex, sy)
        else:
            intermediate = (sx, ey)

        ix, iy = int(intermediate[0]), int(intermediate[1])

        # First segment: start -> corner
        pygame.draw.line(surface, color, (sx, sy), (ix, iy), thickness)

        # Second segment: corner -> arrowhead base (trim for head)
        dx_final = ex - ix
        dy_final = ey - iy
        if dx_final != 0 or dy_final != 0:
            angle = math.atan2(dy_final, dx_final)
            head_length = 15
            base_x = int(ex - head_length * math.cos(angle))
            base_y = int(ey - head_length * math.sin(angle))

            # Overlap the second segment slightly into the head to remove any seam
            overlap = max(1, thickness // 2)
            ox = int(round(overlap * math.cos(angle)))
            oy = int(round(overlap * math.sin(angle)))
            shaft_end_x = base_x + ox
            shaft_end_y = base_y + oy
            pygame.draw.line(surface, color, (ix, iy), (shaft_end_x, shaft_end_y), thickness)

            # Smooth the elbow by covering any gap at the corner
            r = max(1, thickness // 2)
            gfxdraw.filled_circle(surface, ix, iy, r, color)
            gfxdraw.aacircle(surface, ix, iy, r, color)

            # Arrowhead
            head_angle = math.pi / 6
            head_x1 = int(ex - head_length * math.cos(angle - head_angle))
            head_y1 = int(ey - head_length * math.sin(angle - head_angle))
            head_x2 = int(ex - head_length * math.cos(angle + head_angle))
            head_y2 = int(ey - head_length * math.sin(angle + head_angle))
            points = [(ex, ey), (head_x1, head_y1), (head_x2, head_y2)]
            gfxdraw.filled_polygon(surface, points, color)
            gfxdraw.aapolygon(surface, points, color)

    def draw_arrows(self, screen: pygame.Surface):
        # Draw onto an alpha surface to get smooth transparency
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        for arrow in self.arrows:
            start_pos = self._square_to_pixel(arrow.start_square)
            end_pos = self._square_to_pixel(arrow.end_square)
            if arrow.arrow_type == ArrowType.KNIGHT:
                self._draw_knight_arrow(overlay, start_pos, end_pos, arrow.color, arrow.thickness)
            else:
                self._draw_arrow_line(overlay, start_pos, end_pos, arrow.color, arrow.thickness)

        if self.drawing_arrow and self.arrow_start_square:
            current_square = self.current_hover_square or self._candidate_square
            if current_square and not (1 <= current_square[0] <= 8 and 1 <= current_square[1] <= 8):
                current_square = None
            if current_square is not None and current_square != self.arrow_start_square:
                arrow_type = self._determine_arrow_type(self.arrow_start_square, current_square)
                if arrow_type:
                    start_pos = self._square_to_pixel(self.arrow_start_square)
                    end_pos = self._square_to_pixel(current_square)
                    preview_color = (255, 165, 0, 120)
                    preview_thickness = 6
                    if arrow_type == ArrowType.KNIGHT:
                        self._draw_knight_arrow(overlay, start_pos, end_pos, preview_color, preview_thickness)
                    else:
                        self._draw_arrow_line(overlay, start_pos, end_pos, preview_color, preview_thickness)

        # Blit the overlay once
        screen.blit(overlay, (0, 0))
