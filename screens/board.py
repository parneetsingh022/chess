from constants import colors, fonts
import pygame

from utils.screen_manager import ScreenManager
from utils.chess_board_manager import ChessBoardManager
from utils.board_pieces_manager import BoardPiecesManager

class BoardPage:
    def __init__(self, screen: pygame.Surface, screen_manager: ScreenManager):
        self.screen = screen
        self.screen_manager = screen_manager
        self.player = "white"
        self.chess_board_manager = ChessBoardManager(screen, screen.get_width())
        self.board_pieces_manager = BoardPiecesManager(screen)

    def display(self, event: pygame.event.Event) -> None:
        self.screen.fill(colors.BACKGROUND_COLOR)

        # Define the color for the black box
        black_color = (0, 0, 0)
        white_color = (255, 255, 255)

        # if event.type == pygame.MOUSEMOTION:
        #     x, y = event.pos
        #     x,y = self.chess_board_manager.get_square_loc(x, y)
        #     color = self.chess_board_manager.get_square_color(x, y)
        #     print(self.chess_board_manager.get_square_name(x,y))


        self.chess_board_manager.draw_board(black_color, white_color)
        self.board_pieces_manager.display_piece(0, 0, 6,5)
        
        pygame.display.update()