from constants import colors
import pygame
from components.buttons.button import Button
from utils.screen_manager import ScreenManager
from utils.versions.version_reader import read_version_from_file
from states.gamestate import game_state


def quit_button_action():
    pygame.quit()
    quit()

def start_new(screen_manager: ScreenManager):
    game_state.start_new = True
    game_state.in_game = False
    screen_manager.set_screen("board_page")


def resume_game(screen_manager: ScreenManager):
    screen_manager.set_screen("board_page")

class MenuPage:
    def __init__(self, screen: pygame.Surface, screen_manager: ScreenManager):
        self.screen = screen
        self.is_resume_added = False
        self.screen_manager = screen_manager
        
        self.start_button = Button("Start")
        self.start_new_game = Button("New Game")
        self.resume_button = Button("Resume")
        self.settings_button = Button("Settings")
        self.quit_button = Button("Quit")


        self.start_button_item = (self.start_button, lambda: resume_game(screen_manager))
        self.resume_button_item = (self.resume_button, lambda: resume_game(self.screen_manager))
        self.start_new_game_button_item = (self.start_new_game, lambda: start_new(self.screen_manager))
        self.settings_button_item = (self.settings_button, lambda: screen_manager.set_screen("settings"))
        self.quit_button_item = (self.quit_button, quit_button_action)


        self.button_padding = 20
        self.menu_buttons = [
            self.start_button_item,
            self.settings_button_item,
            self.quit_button_item,
        ]

        # Initialize font for version label
        self.font = pygame.font.Font(None, 25)  # You can specify a font file and size

    def display(self, event: pygame.event.Event) -> None:

        self.screen.fill(colors.BACKGROUND_COLOR)

        if game_state.in_game and not self.is_resume_added:
            self.menu_buttons.pop(0)
            self.menu_buttons.insert(
                0, self.resume_button_item
            )

            self.menu_buttons.insert(
                1, self.start_new_game_button_item
            )
            
            
            self.is_resume_added = True

        elif not game_state.in_game and self.is_resume_added:
            self.menu_buttons.pop(0)  # Remove "Resume" button
            self.menu_buttons.pop(0)  # Remove "New Game" button
            self.menu_buttons.insert(0, self.start_button_item)
            self.is_resume_added = False
            

        # Calculate the total height of the menu
        total_menu_height = 0
        for button, _ in self.menu_buttons:
            total_menu_height += button.get_button_height() + self.button_padding

        # Calculate the starting height of the menu
        start_height = (
            self.screen.get_height() - total_menu_height
        ) // 2

        # Display the menu buttons on the screen
        del_y = 0
        for button, _ in self.menu_buttons:
            button.set_position(self.screen.get_width() // 2, start_height + del_y, center=True)
            del_y += button.get_button_height() + self.button_padding

        # Display the menu buttons on the screen
        for button, action in self.menu_buttons:
            button.display(self.screen)
            button.on_click(event, action)
    

        pygame.display.update()