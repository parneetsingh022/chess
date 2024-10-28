import pygame
from constants import colors
from constants import fonts

class SettingsCard:
    def __init__(self, text, width, height=50, clickable=True):
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)  # Enable per-pixel alpha
        self.rect = self.image.get_rect()
        self.color = colors.WHITE_COLOR
        self.text = text
        self.clickable = clickable

        # Initialize font from the specified file
        self.font = fonts.SETTING_FONT_CARD_HEADING
        self.symbol_font = fonts.CHEVRON_RIGHT

    def set_position(self, x, y, center=False):
        if center:
            self.rect.center = (x, y)
        else:
            self.rect.topleft = (x, y)

    def display(self, screen):
        # Fill the image with a transparent color
        self.image.fill((0, 0, 0, 0))
        
        # Draw the rounded rectangle
        pygame.draw.rect(
            self.image,
            self.color,
            self.image.get_rect(),
            border_radius=15  # Adjust the radius as needed
        )
        
        # Render the text
        text_surface = self.font.render(self.text, True, colors.BLACK_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, (self.rect.height - text_rect.height) // 2)  # Padding from the left side
        
        # Blit the text onto the image
        self.image.blit(text_surface, text_rect)
        
        # If clickable, render the "greater than" symbol
        if self.clickable:
            symbol_surface = self.symbol_font.render("›", True, colors.GREY_COLOR)
            symbol_rect = symbol_surface.get_rect()
            symbol_rect.center = (self.rect.width - 30, (self.rect.height // 2) - 5)  # Center the symbol within the card and move it 5 pixels up
            self.image.blit(symbol_surface, symbol_rect)
        
        # Blit the image onto the screen
        screen.blit(self.image, self.rect)