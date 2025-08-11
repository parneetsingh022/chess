from constants import colors
import pygame
from components.buttons.button import Button
from utils.screen_manager import ScreenManager
from utils.resource_path import resource_path
from states.gamestate import game_state
import os
from utils.local_storage.storage import settings_file_manager  # Import the SettingsFileManager class
import threading

def quit_button_action():
    pygame.quit()
    quit()

def start_new(screen_manager: ScreenManager):
    # Ensure any multiplayer state is cleared when starting a solo game
    try:
        if game_state.net_socket:
            try:
                game_state.net_socket.close()
            except Exception:
                pass
        if game_state.advertise_socket:
            try:
                game_state.advertise_socket.close()
            except Exception:
                pass
    finally:
        game_state.multiplayer = False
        game_state.room_code = None
        game_state.is_host = False
        game_state.net_socket = None
        game_state.advertise_socket = None
        game_state.my_color = None
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
        # Multiplayer navigates to its own page
        self.multiplayer_button = Button("Multiplayer")

        self.start_button_item = (self.start_button, lambda: resume_game(screen_manager))
        self.resume_button_item = (self.resume_button, lambda: resume_game(self.screen_manager))
        self.start_new_game_button_item = (self.start_new_game, lambda: start_new(self.screen_manager))
        self.settings_button_item = (self.settings_button, lambda: screen_manager.set_screen("settings"))
        self.quit_button_item = (self.quit_button, quit_button_action)
        self.multiplayer_button_item = (self.multiplayer_button, lambda: self.screen_manager.set_screen("multiplayer"))

        self.button_padding = 20
        self.menu_buttons = [
            self.start_button_item,
            self.multiplayer_button_item,
            self.settings_button_item,
            self.quit_button_item,
        ]
        self.input_popup = None
        # Initialize font for version label
        self.font = pygame.font.Font(None, 25)  # You can specify a font file and size

        self.logo_image = pygame.image.load(resource_path(os.path.join("assets", "icon.png")))
        self.logo_image = self.logo_image.convert_alpha()
        self.cur_size = settings_file_manager.get_setting("win_size")

    def display(self, event: pygame.event.Event) -> None:
        self.screen.fill(colors.BACKGROUND_COLOR)

        # Scale logo based on window size
        if self.cur_size == "small":
            self.logo_image = pygame.transform.smoothscale(self.logo_image, (200, 200))
        else:
            self.logo_image = pygame.transform.smoothscale(self.logo_image, (400, 400))

        # Switch between Start/Resume + New Game depending on game state
        if game_state.in_game and not self.is_resume_added:
            self.menu_buttons.pop(0)
            self.menu_buttons.insert(0, self.resume_button_item)
            self.menu_buttons.insert(1, self.start_new_game_button_item)
            self.is_resume_added = True
        elif not game_state.in_game and self.is_resume_added:
            self.menu_buttons.pop(0)  # Remove "Resume"
            self.menu_buttons.pop(0)  # Remove "New Game"
            self.menu_buttons.insert(0, self.start_button_item)
            self.is_resume_added = False

        # Layout buttons
        total_menu_height = 0
        for button, _ in self.menu_buttons:
            total_menu_height += button.get_button_height() + self.button_padding

        start_height = (self.screen.get_height() - total_menu_height) // 2

        del_y = 0
        for button, _ in self.menu_buttons:
            offset = 100
            if self.cur_size == "small":
                offset = 150
            elif self.cur_size == "large":
                offset = 200
            button.set_position(self.logo_image.get_rect().bottomright[0] + offset, start_height + del_y, center=True)
            del_y += button.get_button_height() + self.button_padding

        # Draw buttons and handle clicks
        for button, action in self.menu_buttons:
            button.display(self.screen)
            button.on_click(event, action)

        # Draw logo centered to the left of the menu
        start_y = self.menu_buttons[0][0].get_start_position()[1]
        end_y = self.menu_buttons[-1][0].get_end_position()[1]
        middle_y = (start_y + end_y) // 2
        logo_height = self.logo_image.get_height()
        logo_start = (middle_y - logo_height // 2)
        self.screen.blit(self.logo_image, (0, logo_start + 10))

        pygame.display.update()