import pygame
from typing import Tuple
from utils.local_storage.storage import settings_file_manager  # Import the SettingsFileManager class
from constants.fonts import BOARD_COORDINATES_FONT
from constants import colors

def draw_square(i, j, square_size, color, screen, board_top_bar_height):
    pygame.draw.rect(screen, color, pygame.Rect(i * square_size, j * square_size + board_top_bar_height, square_size, square_size))

class ChessBoardManager:
    def __init__(self, screen: pygame.Surface, screen_width: int, board_top_bar_height: int, player: str = "white"):
        self.screen = screen
        self.screen_width = screen_width
        self._square_size = screen_width // 8  # Ensure square size is an integer
        self.player = player
        settings_player = settings_file_manager.get_setting("default_player")
        if settings_player is not None:
            self.player = settings_player.lower()

        self.board_top_bar_height = board_top_bar_height
        self.red_color = (200, 0, 0)
        self.color_state = {}  # Dictionary to track the color state of specific squares

        

    def draw_board(self, black_color: Tuple, white_color: Tuple) -> None:
        settings_default_player = settings_file_manager.get_setting("default_player")
        if self.player != settings_default_player and settings_default_player is not None:
            settings_default_player = settings_default_player.lower()
            self.player = settings_default_player

        # Draw squares with orientation-aware mapping so color_state and parity match perspective
        for i in range(0, 8):
            for j in range(0, 8):
                if self.player == "white":
                    bx, by = i + 1, j + 1
                else:
                    bx, by = 8 - i, 8 - j

                base_color = white_color if (bx + by) % 2 == 0 else black_color
                sq_color = self.color_state.get((bx, by), base_color)
                draw_square(i, j, self._square_size, sq_color, self.screen, self.board_top_bar_height)

        # Draw file letters (a–h) along the bottom and rank numbers (1–8) along the left
        pad = max(3, self._square_size // 16)
        # Bottom files
        for i in range(8):
            file_index = i if self.player == "white" else (7 - i)
            letter = chr(ord('a') + file_index)
            surf = BOARD_COORDINATES_FONT.render(letter, True, colors.FONT_COLOR_GREY)
            x = (i + 1) * self._square_size - surf.get_width() - pad
            y = self.board_top_bar_height + 8 * self._square_size - surf.get_height() - pad
            self.screen.blit(surf, (x, y))

        # Left ranks
        for j in range(8):
            rank = (8 - j) if self.player == "white" else (j + 1)
            surf = BOARD_COORDINATES_FONT.render(str(rank), True, colors.FONT_COLOR_GREY)
            x = pad
            y = self.board_top_bar_height + j * self._square_size + pad
            self.screen.blit(surf, (x, y))

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