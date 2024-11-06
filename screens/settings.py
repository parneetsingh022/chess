from constants import colors
import pygame
from utils.screen_manager import ScreenManager
from components.settings.settings_card import SettingsCard,SettingsToggleCard
from constants import fonts
from components.image_button import BackButton
from components.settings.layout.layout import layout_manager
class SettingsPage:
    def __init__(self, screen: pygame.Surface, screen_manager: ScreenManager):
        self.screen = screen
        self.screen_manager = screen_manager
        self.start_position = 20

        self.card_padding = 50
        self.card_width = self.screen.get_width() - (self.card_padding * 2)
        
        # Setting options
        self.setting_options = {}
        
        cur_elements = layout_manager.get_current_layout()['sub_layout']
        for key, value in cur_elements.items():
            self.setting_options[key] = {
                'type': value['type']
            }

        # Initialize SettingsCards
        self.settings_cards = []
        for key, options in self.setting_options.items():
            if options['type'] == 'category':
                card = SettingsCard(key, self.card_width)
            elif options['type'] == 'toggle':
                card = SettingsToggleCard(key, self.card_width)
            self.settings_cards.append(card)

        # Initialize font for the title
        self.title_font = fonts.SETTINGS_HEADING

        # Initialize Home button as a BackButton
        self.home_button = BackButton()
        self.home_button.set_position(10, 10)  # Position at the top-left corner

        

        

    def set_start_position(self, factor: int) -> None:
        factor *= 30
        self.start_position += factor
        if self.start_position > 20: self.start_position = 20

    def display(self, event: pygame.event.Event) -> None:
        self.screen.fill(colors.BACKGROUND_COLOR)
        
        # Render and display the title
        title_surface = self.title_font.render("Settings", True, colors.BLACK_COLOR)
        title_rect = title_surface.get_rect()
        title_rect.centerx = self.screen.get_width() // 2
        title_rect.top = self.start_position
        self.screen.blit(title_surface, title_rect)
        
        # Display the Home button
        self.home_button.set_position(10, self.start_position)
        self.home_button.display(self.screen)
        self.home_button.on_click(event, lambda: self.screen_manager.set_screen("menu"))

        # Display the SettingsCards
        for i, card in enumerate(self.settings_cards):
            card.set_position(self.card_padding, self.start_position + 80 + i * 65)  # Update position based on start_position
            card.display(self.screen)
            card.on_click(event)

        pygame.display.update()