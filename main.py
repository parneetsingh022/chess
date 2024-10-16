import pygame
import sys
import os
import constants.colors as colors

from screens.menu import MenuPage
from screens.board import BoardPage

from utils import screen_manager
from utils.board_theme_reader import ThemeReader

theme = ThemeReader()

pygame.init()

screen = pygame.display.set_mode((650, 650))
pygame.display.set_caption("Chess")

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

current_screen = "board_page"

screen_manager = screen_manager.ScreenManager(screen)

# Create screens and add them to the ScreenManager
menu_page = MenuPage(screen, screen_manager)
board_page = BoardPage(screen, screen_manager)

screen_manager.add_screen("menu", menu_page)
screen_manager.add_screen("board_page", board_page)

# Set the initial screen
screen_manager.set_screen("menu")

# Create a Clock object to control the frame rate
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    #     if event.type == pygame.KEYDOWN:
    #         if event.key == pygame.K_m:  # Press 'm' to go to menu
    #             current_screen = "menu"
    #         if event.key == pygame.K_s:  # Press 's' to go to settings
    #             current_screen = "settings"
    
        screen_manager.display_current_screen(event)
    
    # Control the frame rate
    clock.tick(60)  # Limit to 60 frames per second