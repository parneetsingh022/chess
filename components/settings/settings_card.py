import pygame
from constants import colors
from constants import fonts
from components.settings.toggle_button import ToggleButton  # Import the ToggleButton class

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

        # Track mouse state
        self.mouse_down = False

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

    def on_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button down
            if self.rect.collidepoint(event.pos):
                self.mouse_down = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left mouse button up
            if self.mouse_down and self.rect.collidepoint(event.pos):
                print("hello")
            self.mouse_down = False

class SettingsToggleCard(SettingsCard):
    def __init__(self, text, width, height=50, clickable=True, toggle_button_size=(50, 50)):
        super().__init__(text, width, height, clickable)
        self.toggle_button = ToggleButton(self.image, width - toggle_button_size[0] - 10, (height - toggle_button_size[1]) // 2, size=toggle_button_size)
        self.clicked = False
        self.state = False

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
        
        # Display the toggle button
        self.toggle_button.display()
        
        # Blit the image onto the screen
        screen.blit(self.image, self.rect)

    def on_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and not self.clicked:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP and self.clicked:
            if self.rect.collidepoint(event.pos):
                self.clicked = False
                self.state = not self.state
                self.toggle_button.set_state(self.state)