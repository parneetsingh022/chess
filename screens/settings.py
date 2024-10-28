from constants import colors
import pygame
from components.buttons.button import Button
from utils.screen_manager import ScreenManager
from utils.versions.version_reader import read_version_from_file

from components.settings.settings_card import SettingsCard

class SettingsPage:
    def __init__(self, screen: pygame.Surface, screen_manager: ScreenManager):
        self.screen = screen
        self.screen_manager = screen_manager

        self.card_padding = 50
        self.card_width = self.screen.get_width() - (self.card_padding * 2)
        
        # Initialize SettingsCard
        self.settings_card = SettingsCard(self.card_width)  # Example dimensions
        self.settings_card.set_position(self.card_padding, 50)  # Example position

    def display(self, event: pygame.event.Event) -> None:
        self.screen.fill(colors.BACKGROUND_COLOR)
        
        # Display the SettingsCard
        self.settings_card.display(self.screen)

        pygame.display.update()