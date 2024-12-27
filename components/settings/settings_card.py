import pygame
from constants import colors
from constants import fonts
from components.settings.toggle_button import ToggleButton  # Import the ToggleButton class
from utils.local_storage.storage import settings_file_manager  # Import the SettingsFileManager class

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

    def on_click(self, event, layout_manager) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button down
            if self.rect.collidepoint(event.pos):
                self.mouse_down = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left mouse button up
            if self.mouse_down and self.rect.collidepoint(event.pos):
                layout_manager.move_to_sub_layout(self.text)
                self.mouse_down = False
                return True
            self.mouse_down = False

        return False
    
    def bottom_pos(self) -> int:
        return self.rect.bottom

class SettingsToggleCard(SettingsCard):
    def __init__(self, text, width, height=50, clickable=True, toggle_button_size=(50, 50)):
        super().__init__(text, width, height, clickable)
        self.toggle_button = ToggleButton(self.image, width - toggle_button_size[0] - 10, (height - toggle_button_size[1]) // 2, size=toggle_button_size)
        self.clicked = False
        self.state = False
        self.target_atrb = None

    def set_toggle(self, state):
        self.state = state

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
        self.toggle_button.set_state(self.state)
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

                if self.target_atrb is not None:
                    settings_file_manager.save_setting(self.target_atrb, self.state)

class SettingsTextCard(SettingsCard):
    def __init__(self, text, right_text, width, height=50):
        super().__init__(text, width, height, clickable=False)
        self.right_text = right_text
        self.right_text_font = fonts.SETTING_FONT_CARD_SUBTEXT

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
        
        # Render the main text
        text_surface = self.font.render(self.text, True, colors.BLACK_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (10, (self.rect.height - text_rect.height) // 2)  # Padding from the left side
        
        # Blit the main text onto the image
        self.image.blit(text_surface, text_rect)
        
        # Render the right-aligned text
        right_text_surface = self.right_text_font.render(self.right_text, True, colors.GREY_COLOR)
        right_text_rect = right_text_surface.get_rect()
        right_text_rect.topright = (self.rect.width - 10, (self.rect.height - right_text_rect.height) // 2)  # Padding from the right side
        
        # Blit the right-aligned text onto the image
        self.image.blit(right_text_surface, right_text_rect)
        
        # Blit the image onto the screen
        screen.blit(self.image, self.rect)

class SettingsOptionCard(SettingsCard):
    def __init__(self, text, default_options, width, height=50, restart=False):
        super().__init__(text, width, height, clickable=True)
        self.clicked = False
        self.target_atrb = None
        self.right_text_font = fonts.SETTING_FONT_CARD_SUBTEXT
        self.restart_text_font = fonts.SETTING_SUBMESSAGE
        self.right_text = None
        self.options = default_options
        self.loaded_settings = False
        self.restart = restart
        self.show_restart_message = False

    def set_toggle(self, state):
        self.state = state

    def display(self, screen):
        if self.right_text is None:
            self.right_text = self.options[0] if self.options else ""
        if settings_file_manager.get_setting(self.target_atrb) is not None and self.loaded_settings == False:
            self.right_text = settings_file_manager.get_setting(self.target_atrb)
            self.loaded_settings = True

        # Fill the image with a transparent color
        self.image.fill((0, 0, 0, 0))
        
        # Draw the rounded rectangle
        pygame.draw.rect(
            self.image,
            self.color,
            self.image.get_rect(),
            border_radius=15  # Adjust the radius as needed
        )
        
        # Render the main text
        text_surface = self.font.render(self.text, True, colors.BLACK_COLOR)
        text_rect = text_surface.get_rect()
        offset = 10 if self.show_restart_message else 0
        text_rect.topleft = (10, ((self.rect.height - text_rect.height) // 2) - offset)  # Padding from the left side
        
        # Blit the main text onto the image
        self.image.blit(text_surface, text_rect)
        
        # Render the right-aligned text
        right_text_surface = self.right_text_font.render(self.right_text.capitalize(), True, colors.BLACK_COLOR)
        right_text_rect = right_text_surface.get_rect()
        right_text_rect.topright = (self.rect.width - 10, (self.rect.height - right_text_rect.height) // 2)  # Padding from the right side
        
        # Blit the right-aligned text onto the image
        self.image.blit(right_text_surface, right_text_rect)
        
        
        restart_text_surface = self.restart_text_font.render("Restart required for this to take effect", True, (255, 0, 0))
        restart_text_rect = restart_text_surface.get_rect()
        restart_text_rect.topleft = (10, text_rect.bottom)  # Position below the main text
        if self.show_restart_message:
            self.image.blit(restart_text_surface, restart_text_rect)
        # Blit the image onto the screen
        screen.blit(self.image, self.rect)

    def on_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and not self.clicked:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP and self.clicked:
            if self.rect.collidepoint(event.pos):
                self.clicked = False
                pos = self.options.index(self.right_text.lower())
                pos = (pos + 1) % len(self.options)
                self.right_text = self.options[pos]
                if self.target_atrb is not None:
                    settings_file_manager.save_setting(self.target_atrb, self.right_text)
                if self.restart:
                    self.show_restart_message = True