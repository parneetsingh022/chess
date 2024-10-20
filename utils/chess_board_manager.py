import pygame
from typing import Tuple

def draw_square(x: int, y: int, square_size, color: Tuple[int], screen: pygame.Surface) -> None:
    pygame.draw.rect(screen, color, (x * square_size, y * square_size, square_size, square_size))

class ChessBoardManager:
    def __init__(self, screen: pygame.Surface, screen_width: int, player: str = "black"):
        self.screen = screen
        self.screen_width = screen_width
        self._square_size = screen_width // 8 + 0.5
        self.player = player

    def draw_board(self, black_color: Tuple, white_color: Tuple) -> None:
        for i in range(0, 8):
            for j in range(0, 8):
                color1, color2 = (white_color, black_color) if (i + j) % 2 == 0 else (black_color, white_color)
                
                if self.player == "white":
                    color = color1
                else:
                    color = color2
                    
                draw_square(i, j, self._square_size, color, self.screen)

    def get_square_loc(self, x, y):
        """
        Convert screen coordinates to board coordinates.
        """
        board_x = x // self._square_size + 1
        board_y = y // self._square_size + 1
        if self.player == "black":
            board_x = 9 - board_x
            board_y = 9 - board_y
        return (board_x, board_y)