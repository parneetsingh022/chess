from constants import colors, fonts
import pygame

from utils.screen_manager import ScreenManager
from utils.chess_board_manager import ChessBoardManager
from utils.board_pieces_manager import BoardPiecesManager

from components.image_button import ImageButton, BackButton, SettingsButton, RestartButton
from enum import Enum
from states.gamestate import game_state


class TopBarButtonType(Enum):
    LEFTBUTTON = 1
    RIGHTBUTTON = 2

class TopBarButtonItem:
    def __init__(self, button : ImageButton, action, type : TopBarButtonType):
        self.button = button()
        self.action = action
        self.type = type

def settings_button_action(screen_manager: ScreenManager):
    screen_manager.set_screen("settings")
    game_state.board_settings_button_pressed = True

def back_button_action(screen_manager: ScreenManager):
    screen_manager.set_screen("menu")

def restart_button_action(board_pieces_manager: BoardPiecesManager):
    if not game_state.in_game: return

    board_pieces_manager.reset(show_p=True)

class BoardPage:

    def __init__(self, screen: pygame.Surface, screen_manager: ScreenManager, board_top_bar_height: int):
        self.screen = screen
        self.board_top_bar_height = board_top_bar_height
        self.screen_manager = screen_manager
        self.chess_board_manager = ChessBoardManager(screen, screen.get_width(), self.board_top_bar_height)
        self.board_pieces_manager = BoardPiecesManager(screen, self.chess_board_manager._square_size, self.chess_board_manager.player, self.board_top_bar_height)
        
        self.mouse_down = False


        self.home_button = TopBarButtonItem(BackButton, lambda: back_button_action(self.screen_manager), TopBarButtonType.LEFTBUTTON)
        self.restart_button = TopBarButtonItem(RestartButton, lambda: restart_button_action(self.board_pieces_manager), TopBarButtonType.LEFTBUTTON)
        self.settings_button = TopBarButtonItem(SettingsButton, lambda: settings_button_action(self.screen_manager), TopBarButtonType.RIGHTBUTTON)

        self.top_bar_buttons = [
            self.home_button,
            self.restart_button,
            self.settings_button,
        ]

        left_buttons = [btn for btn in self.top_bar_buttons if btn.type == TopBarButtonType.LEFTBUTTON]
        right_buttons = [btn for btn in self.top_bar_buttons if btn.type == TopBarButtonType.RIGHTBUTTON]

        last_left_button_pos = 0
        for btn in left_buttons:
            btn.button.set_position(last_left_button_pos + 10, 10)
            last_left_button_pos = btn.button.end_pos()

        last_right_button_pos = self.screen.get_width()
        for btn in right_buttons:
            btn.button.set_position(last_right_button_pos - 40, 10)
            last_right_button_pos = btn.button.start_pos()

    def display(self, event: pygame.event.Event) -> None:
        if game_state.check_position is not None:
            self.chess_board_manager.set_color_red(*game_state.check_position)
        else:
            self.chess_board_manager.unset_color_red()

        self.board_pieces_manager.add_event(event)
        # Fill screen and draw all components
        self.screen.fill(colors.BACKGROUND_COLOR)
        
        for btn in self.top_bar_buttons:
            if btn == self.restart_button and not game_state.in_game:
                btn.button.disable()
            elif btn == self.restart_button and game_state.in_game and btn.button.disabled == True:
                btn.button.enable()

            btn.button.display(self.screen)
            if not game_state.pop_up_on:
                btn.button.on_click(event, btn.action)
            else:
                btn.button.on_click(event, lambda: None)
        black_color = (0, 0, 0)
        white_color = (255, 255, 255)

        self.chess_board_manager.draw_board(black_color, white_color)
        self.board_pieces_manager.display()

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
