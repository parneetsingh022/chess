import pygame
import sys
import os
import constants.colors as colors

from screens.menu import MenuPage
from screens.board import BoardPage
from screens.settings import SettingsPage
from screens.waiting import WaitingPage
from screens.multiplayer import MultiplayerPage

from utils import screen_manager
from utils.window_manager import window_manager
from utils.board_theme_reader import ThemeReader
from utils.resource_path import resource_path

# Determine the base directory and append it to sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

theme = ThemeReader()

pygame.init()

BOARD_TOP_BAR_HEIGHT = 50

# Initialize window manager and create screen
window_manager.board_top_bar_height = BOARD_TOP_BAR_HEIGHT
screen = window_manager.initialize_screen()
pygame.display.set_caption("Chess")

# Load and set the icon
icon_path = resource_path("assets/icon.png")  # Path to your icon image
icon = pygame.image.load(icon_path)
pygame.display.set_icon(icon)


current_screen = "menu"

screen_manager = screen_manager.ScreenManager(screen)

# Set window manager reference to screen manager
window_manager.set_screen_manager(screen_manager)

# Create screens and add them to the ScreenManager
menu_page = MenuPage(screen, screen_manager)
board_page = BoardPage(screen, screen_manager, BOARD_TOP_BAR_HEIGHT)
settings_page = SettingsPage(screen, screen_manager)
waiting_page = WaitingPage(screen, screen_manager)
multiplayer_page = MultiplayerPage(screen, screen_manager)

screen_manager.add_screen("menu", menu_page)
screen_manager.add_screen("board_page", board_page)
screen_manager.add_screen("settings", settings_page)
screen_manager.add_screen("waiting", waiting_page)
screen_manager.add_screen("multiplayer", multiplayer_page)

# Set the initial screen
screen_manager.set_screen(current_screen)

# Create a Clock object to control the frame rate
clock = pygame.time.Clock()

mouse_button_scroll = 0
while True:
    # Check for window size changes and apply them instantly
    window_manager.check_and_apply_size_change()
    
    had_event = False
    for event in pygame.event.get():
        had_event = True
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle other events only if the popup is not visible
        if event.type == pygame.MOUSEBUTTONDOWN and screen_manager.current_screen == settings_page:
            if event.button == 4:  # Mouse wheel up
                settings_page.set_start_position(1)
            elif event.button == 5:  # Mouse wheel down
                settings_page.set_start_position(-1)

        # Dispatch this event to the current screen so popups receive KEYDOWN
        screen_manager.display_current_screen(event)

    # If there were no events this frame, still draw/update the current screen
    if not had_event:
        screen_manager.display_current_screen(None)

    # Control the frame rate
    clock.tick(60)  # Limit to 60 frames per second