import pygame
from constants import colors, fonts
from typing import Callable

class Button:
    def __init__(self, text: str, padding: int = 10, border=False):
        self.text_string = text
        self.font_color = colors.FONT_COLOR_BLACK
        self.border_color = colors.FONT_COLOR_BLACK
        self.font = fonts.DEFAULT_FONT
        self.padding = padding
        self.is_pressed = False # used for button press
        self.border = border
        self.disable = False
        # Create and set the initial text
        self.update_text(text)

    def update_text(self, text: str):
        # Render the text
        self.text = self.font.render(text, True, self.font_color)
        self.text_rect = self.text.get_rect()

        if self.border:
            # Update the button rectangle based on text size and padding
            self.button_rect = self.text_rect.inflate(2 * self.padding, 2 * self.padding)

            # Center the text within the button_rect
            self.text_rect.center = self.button_rect.center
        else:
            self.button_rect = self.text_rect

    def set_position(self, x: int, y: int, center: bool = False):
        if center:
            self.button_rect.center = (x, y)
        else:
            self.button_rect.topleft = (x, y)

        # Center the text within the button_rect after setting position
        self.text_rect.center = self.button_rect.center

    def display(self, screen: pygame.Surface):
        # Draw the button rectangle (border)
        if self.border:
            pygame.draw.rect(screen, self.border_color, self.button_rect, 2)

        # Draw the text on the screen
        screen.blit(self.text, self.text_rect)

    def clear(self, screen: pygame.Surface, background_color: tuple = colors.BACKGROUND_COLOR):
        # Clear the previous button area by filling the area with the background color
        pygame.draw.rect(screen, background_color, self.button_rect)

    def on_click(self, event: pygame.event.Event, fnc: Callable[[], None]) -> bool:
        if self.disable: return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed:
                if self.button_rect.collidepoint(event.pos):
                    fnc()

                self.is_pressed = False
                return True
        return False

    def disable_button(self):
        self.disable = True
        self.font_color = colors.FONT_COLOR_GREY
        self.border_color = colors.FONT_COLOR_GREY
        self.update_text(self.text_string)
        