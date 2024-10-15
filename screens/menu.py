from constants import colors
import pygame
from components.buttons.button import Button


def start_button_action():
    print("Going to game")

def quit_button_action():
    pygame.quit()
    quit()



class MenuPage:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        
        self.start_button = Button("Start")
        self.quit_button = Button("Quit")

    def display(self, event : pygame.event.Event) -> None:
        self.screen.fill(colors.BACKGROUND_COLOR)

        self.start_button.display(self.screen)
        self.start_button.set_position(
            self.screen.get_width()//2, 
            self.screen.get_height()//3, 
            center=True
        )
        self.start_button.on_click(event, start_button_action)


        self.quit_button.set_position(
            self.screen.get_width()//2, 
            self.screen.get_height()//3 + 60, 
            center=True
        )
        self.quit_button.display(self.screen)
        self.quit_button.on_click(event, quit_button_action)

        pygame.display.update()