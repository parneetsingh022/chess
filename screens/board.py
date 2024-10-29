from constants import colors, fonts
import pygame

from utils.screen_manager import ScreenManager
from utils.chess_board_manager import ChessBoardManager
from utils.board_pieces_manager import BoardPiecesManager
from components.turn_indicator import TurnIndicator

from components.image_button import BackButton


class BoardPage:
    def __init__(self, screen: pygame.Surface, screen_manager: ScreenManager, board_top_bar_height: int):
        self.screen = screen
        self.board_top_bar_height = board_top_bar_height
        self.screen_manager = screen_manager
        self.chess_board_manager = ChessBoardManager(screen, screen.get_width(), self.board_top_bar_height)
        self.board_pieces_manager = BoardPiecesManager(screen, self.chess_board_manager._square_size, self.chess_board_manager.player, self.board_top_bar_height)
        

        # self.turn_indicator_height = 50
        # self.turn_indicator = TurnIndicator(self.screen.get_width(), self.turn_indicator_height)

        self.mouse_down = False

        self.home_button = BackButton()
        self.home_button.set_position(10, 10)  # Position at the top-left corner

    def display(self, event: pygame.event.Event) -> None:
        # Fill screen and draw all components
        self.screen.fill(colors.BACKGROUND_COLOR)
        
        self.home_button.display(self.screen)
        self.home_button.on_click(event, lambda: self.screen_manager.set_screen("menu"))
        
        black_color = (0, 0, 0)
        white_color = (255, 255, 255)

        self.chess_board_manager.draw_board(black_color, white_color)
        self.board_pieces_manager.display()
        
        # if self.chess_board_manager.player == "white":
        #     if self.board_pieces_manager.turn == "white":
        #         self.turn_indicator.set_position(0, self.screen.get_height() - self.turn_indicator_height)
        #     else:
        #         self.turn_indicator.set_position(0, self.board_top_bar_height)
        # else:  # self.chess_board_manager.player == "black"
        #     if self.board_pieces_manager.turn == "black":
        #         self.turn_indicator.set_position(0, self.screen.get_height() - self.turn_indicator_height)
        #     else:
        #         self.turn_indicator.set_position(0, self.board_top_bar_height)

        #self.turn_indicator.display(self.screen)
        pygame.display.update()


        # Handle mouse events for interaction
        if event:
            if event.type == pygame.MOUSEBUTTONDOWN and not self.mouse_down:
                self.mouse_down = True
            elif event.type == pygame.MOUSEBUTTONUP and self.mouse_down:
                self.mouse_down = False
                x, y = event.pos
                square_pos = self.chess_board_manager.get_square_loc(x, y)

                if self.board_pieces_manager.selected_piece:
                    self.board_pieces_manager.move_piece(square_pos)
                else:
                    self.board_pieces_manager.select_piece(square_pos)
