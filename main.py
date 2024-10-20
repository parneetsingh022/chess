import pygame
import sys
import os
import constants.colors as colors

from screens.menu import MenuPage
from screens.board import BoardPage

from utils import screen_manager
from utils.board_theme_reader import ThemeReader

# Determine the base directory and append it to sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

theme = ThemeReader()

pygame.init()

# Set up the screen with double buffering
screen = pygame.display.set_mode((650, 650), pygame.DOUBLEBUF)
pygame.display.set_caption("Chess")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

current_screen = "menu"

screen_manager = screen_manager.ScreenManager(screen)

# Create screens and add them to the ScreenManager
menu_page = MenuPage(screen, screen_manager)
board_page = BoardPage(screen, screen_manager)

screen_manager.add_screen("menu", menu_page)
screen_manager.add_screen("board_page", board_page)

# Set the initial screen
screen_manager.set_screen(current_screen)

# Create a Clock object to control the frame rate
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
    
    # Clear the screen
    screen.fill(colors.BACKGROUND_COLOR)
    
    screen_manager.display_current_screen(event)
    # Update the display
    pygame.display.flip()
    
    # Control the frame rate
    clock.tick(60)  # Limit to 60 frames per second