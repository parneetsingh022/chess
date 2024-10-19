import pygame
from typing import Tuple

def draw_square(x : int, y :int, square_size, color : Tuple[int], screen: pygame.Surface) -> None:
    pygame.draw.rect(screen, color, (x * square_size, y * square_size, square_size, square_size))



class ChessBoardManager:
    def __init__(self, screen: pygame.Surface, screen_width: int, player : str = "white"):
        self.screen = screen
        self.screen_width = screen_width
        self._square_size = screen_width // 8 + 0.5
        self.player = player

    def draw_board(self, black_color: Tuple, white_color: Tuple) -> None:
        """
        Draws the chessboard on the screen.

        This method iterates over the board coordinates and draws each square
        with the appropriate color based on the player's perspective and the 
        standard chessboard pattern.

        Args:
            black_color (Tuple): The RGB color tuple for the black squares.
            white_color (Tuple): The RGB color tuple for the white squares.

        Returns:
            None
        """
        for i in range(0, 8):
            for j in range(0, 8):
                color = white_color if (i + j) % 2 == 0 else black_color
                    
                draw_square(i, j, self._square_size, color, self.screen)
                

    def get_loc(self, x: int, y: int) -> Tuple[int, int]:
        """
        Convert board coordinates to pixel coordinates.

        Args:
            x (int): The row on the board.
            y (int): The column on the board.

        Returns:
            Tuple[int, int]: The pixel coordinates (x, y).
        """
        x -= 1
        y -= 1
        return x * self._square_size, y * self._square_size

    def get_square_loc(self, x: int, y: int) -> Tuple[int, int]:
        """
        Convert pixel coordinates to board coordinates.

        Args:
            x (int): The x-coordinate in pixels.
            y (int): The y-coordinate in pixels.

        Returns:
            Tuple[int, int]: The board coordinates (row, column).
        """
        return (x // self._square_size) + 1, (y // self._square_size) + 1
    
    def get_square_name(self, x: int, y: int) -> str:
        """
        Get the name of the square at the given board coordinates.

        Args:
            x (int): The row on the board.
            y (int): The column on the board.

        Returns:
            str: The name of the square (e.g., "a1", "h8").
        """
        x = int(x) - 1
        y = int(y) - 1

        if self.player == "white":
            file_name = chr(97 + x)
            rank_name = str(8 - y)
        else:
            file_name = chr(97 + (7 - x))
            rank_name = str(y + 1)

        return file_name + rank_name

    def get_square_color(self, x: int, y: int) -> str:
        """
        Get the color of the square at the given board coordinates.

        Args:
            x (int): The row on the board.
            y (int): The column on the board.

        Returns:
            str: The color of the square ("white" or "black").
        """
        color = "white" if (x + y) % 2 == 0 else "black"

        if self.player != "white":
            return "white" if color == "black" else "black"

        return color
    
    def get_square_size(self) -> int:
        """
        Get the size of a square on the chessboard.

        Returns:
            int: The size of a square.
        """
        return self._square_size