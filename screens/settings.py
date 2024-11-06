from constants import colors
import pygame
from utils.screen_manager import ScreenManager
from components.settings.settings_card import SettingsCard, SettingsToggleCard
from constants import fonts
from components.image_button import BackButton
from components.settings.layout.layout import layout_manager, LayoutType
from utils.local_storage.storage import settings_file_manager

class SettingsPage:
    def __init__(self, screen: pygame.Surface, screen_manager: ScreenManager):
        self.screen = screen
        self.screen_manager = screen_manager
        self.start_position = 20

        self.card_padding = 50
        self.card_width = self.screen.get_width() - (self.card_padding * 2)

        self.settings_cards = []

        # Initialize font for the title
        self.title_font = fonts.SETTINGS_HEADING

        # Initialize Home button as a BackButton
        self.home_button = BackButton()
        self.home_button.set_position(10, 10)  # Position at the top-left corner

        # Flag to prevent multiple clicks
        self.navigation_in_progress = False



        # Initialize layout
        self._init_layout()

    def _reset_start_position(self) -> None:
        self.start_position = 20

    def _init_layout(self) -> None:
        setting_options = {}
        self.settings_cards = []

        cur_elements = layout_manager.get_current_layout()['sub_layout']
        for key, value in cur_elements.items():
            setting_options[key] = {
                'type': value['type'],
                'target_atrb': value['target_atrb'],
                'value': settings_file_manager.get_setting(value['target_atrb'])
            }


        for key, options in setting_options.items():
            card = None
            if options['type'] == LayoutType.LayoutCategory.value:
                card = SettingsCard(key, self.card_width)
            elif options['type'] == LayoutType.LayoutToggle.value:
                card = SettingsToggleCard(key, self.card_width)
                card.set_toggle(options['value'])
                card.target_atrb = options['target_atrb']

            if card is not None:
                self.settings_cards.append([card, options['type']])

    def set_start_position(self, factor: int) -> None:
        factor *= 30
        self.start_position += factor
        if self.start_position > 20:
            self.start_position = 20

    def _back_btn_fnc(self) -> None:
        if self.navigation_in_progress:
            return
        self.navigation_in_progress = True

        try:
            move = layout_manager.move_to_parent_layout()
            self._reset_start_position()
            if not move:
                self.screen_manager.set_screen("menu")
            else:
                self._init_layout()
        finally:
            # Allow clicks again after a short delay
            pygame.time.set_timer(pygame.USEREVENT, 100)

    def display(self, event: pygame.event.Event) -> None:
        if event.type == pygame.USEREVENT:
            self.navigation_in_progress = False
            pygame.time.set_timer(pygame.USEREVENT, 0)
        
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
        self.home_button.on_click(event, self._back_btn_fnc)

        # Display the SettingsCards
        for i, [card, card_type] in enumerate(self.settings_cards):
            card.set_position(self.card_padding, self.start_position + 80 + i * 65)
            card.display(self.screen)

            if card_type == LayoutType.LayoutCategory.value:
                clicked = card.on_click(event, layout_manager)
                if clicked:
                    self._init_layout()
            elif card_type == LayoutType.LayoutToggle.value:
                card.on_click(event)

        pygame.display.update()