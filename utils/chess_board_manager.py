import pygame
from typing import Tuple

def draw_square(i, j, square_size, color, screen, board_top_bar_height):
    pygame.draw.rect(screen, color, pygame.Rect(i * square_size, j * square_size + board_top_bar_height, square_size, square_size))

class ChessBoardManager:
    def __init__(self, screen: pygame.Surface, screen_width: int, board_top_bar_height: int, player: str = "black"):
        self.screen = screen
        self.screen_width = screen_width
        self._square_size = screen_width // 8  # Ensure square size is an integer
        self.player = player
        self.board_top_bar_height = board_top_bar_height
        self.red_color = (200, 0, 0)
        self.color_state = {}  # Dictionary to track the color state of specific squares

    def draw_board(self, black_color: Tuple, white_color: Tuple) -> None:
        for i in range(0, 8):
            for j in range(0, 8):
                color1, color2 = (white_color, black_color) if (i + j) % 2 == 0 else (black_color, white_color)
                
                if self.player == "white":
                    default_color = color1
                else:
                    default_color = color2

                # Check if the square is set to red
                color = self.color_state.get((i + 1, j + 1), default_color)

                # Adjust the y-coordinate by adding board_top_bar_height
                draw_square(i, j, self._square_size, color, self.screen, self.board_top_bar_height)

    def get_square_loc(self, x, y):
        """
        Convert screen coordinates to board coordinates.
        """
        board_x = x // self._square_size + 1
        board_y = (y - self.board_top_bar_height) // self._square_size + 1
        if self.player == "black":
            board_x = 9 - board_x
            board_y = 9 - board_y
        return (board_x, board_y)

    def set_color_red(self, x, y):
        """
        Set the color of the square at (x, y) to red.
        """
        self.color_state[(x, y)] = self.red_color

    def unset_color_red(self, x=None, y=None):
        """
        Reset the color of the square at (x, y) to its default color.
        If x and y are not provided, reset all squares with red color.
        """
        if x is not None and y is not None:
            if (x, y) in self.color_state:
                del self.color_state[(x, y)]
        else:
            # Remove all entries with red color
            self.color_state = {key: value for key, value in self.color_state.items() if value != self.red_color}