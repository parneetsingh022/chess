import pygame
from constants import colors
from constants import fonts

class SettingsCard:
    def __init__(self, width, height=60, text="Board"):
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.color = colors.WHITE_COLOR
        self.text = text

        # Initialize font from the specified file
        self.font = fonts.SETTING_FONT_CARD_HEADING

    def set_position(self, x, y, center=False):
        if center:
            self.rect.center = (x, y)
        else:
            self.rect.topleft = (x, y)

    def display(self, screen):
        self.image.fill(self.color)
        
        # Render the text
        text_surface = self.font.render(self.text, True, colors.BLACK_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, (self.rect.height - text_rect.height) // 2)  # Padding from the left side
        
        # Blit the text onto the image
        self.image.blit(text_surface, text_rect)
        
        # Blit the image onto the screen
        screen.blit(self.image, self.rect)