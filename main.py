import pygame
import sys
import constants.colors as colors

from screens.menu import MenuPage

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Chess")



WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

current_screen = "menu"

menu_page = MenuPage(screen)

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
    
        # # Display the current screen
        if current_screen == "menu":
            menu_page.display(event)