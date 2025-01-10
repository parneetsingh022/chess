from constants import colors
import pygame
from utils.screen_manager import ScreenManager
from components.settings.settings_card import (
    SettingsCard, 
    SettingsToggleCard, 
    SettingsTextCard, 
    SettingsOptionCard
)
from constants import fonts
from components.image_button import BackButton
from components.settings.layout.layout import layout_manager, LayoutType
from utils.local_storage.storage import settings_file_manager
from states.gamestate import game_state
import time

class ScrollBar:
    def __init__(self, screen: pygame.Surface, height: int, settings_page: 'SettingsPage'):
        self.screen = screen
        self.height = height
        self.default_width = 10
        self.hover_width = 10
        self.width = self.default_width
        self.x = self.screen.get_width() - self.width - 10
        self.y = 10
        self.scroll_height = 100  # Height of the scroll handle
        self.scroll_y = self.y
        self.dragging = False
        self.settings_page = settings_page

    def set_position(self, y: int):
        self.scroll_y = y

    def display(self):
        # Check if the mouse is over the scroll bar
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if pygame.Rect(self.x, self.y, self.width, self.height).collidepoint(mouse_x, mouse_y):
            self.width = self.hover_width
        else:
            self.width = self.default_width

        self.x = self.screen.get_width() - self.width - 10

        # Draw the scroll bar background
        pygame.draw.rect(self.screen, colors.GREY_COLOR, (self.x, self.y, self.width, self.height))
        
        # Draw the scroll handle with rounded edges
        handle_rect = pygame.Rect(self.x, self.scroll_y, self.width, self.scroll_height)
        pygame.draw.rect(self.screen, colors.BLACK_COLOR, handle_rect)
        pygame.draw.circle(self.screen, colors.BLACK_COLOR, (self.x + self.width // 2, self.scroll_y), self.width // 2)
        pygame.draw.circle(self.screen, colors.BLACK_COLOR, (self.x + self.width // 2, self.scroll_y + self.scroll_height), self.width // 2)

    def on_click(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(self.x, self.scroll_y, self.width, self.scroll_height).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging and pygame.mouse.get_pressed()[0]:
            self.scroll_y = max(self.y, min(self.y + self.height - self.scroll_height, event.pos[1]))
            scroll_factor = self.get_scroll_factor()
            self.settings_page.update_start_position(scroll_factor)

    def get_scroll_factor(self):
        return (self.scroll_y - self.y) / (self.height - self.scroll_height)


class SettingsPage:
    def __init__(self, screen: pygame.Surface, screen_manager: ScreenManager):
        self.screen = screen
        self.screen_manager = screen_manager
        self.start_position = 20
        self.end_position = 0

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

        # Attribute to store the bottom card's position
        self.bottom_card_position = 0

        # Initialize layout
        self._init_layout()

        # Initialize scroll bar
        self.scroll_bar = ScrollBar(self.screen, self.screen.get_height() - 20, self)

    def _reset_start_position(self) -> None:
        self.start_position = 20

    def _init_layout(self) -> None:
        setting_options = {}
        self.settings_cards = []

        cur_elements = layout_manager.get_current_layout()['sub_layout']
        for key, value in cur_elements.items():
            val = value['target_atrb'] if LayoutType.LayoutText.value == value['type'] else settings_file_manager.get_setting(value['target_atrb'])
            setting_options[key] = {
                'type': value['type'],
                'target_atrb': value['target_atrb'],
                'value': val,
                'options': value['options'] if 'options' in value else []
            }
        

        for key, options in setting_options.items():
            card = None
            if options['type'] == LayoutType.LayoutCategory.value:
                card = SettingsCard(key, self.card_width)
            elif options['type'] == LayoutType.LayoutToggle.value:
                card = SettingsToggleCard(key, self.card_width)
                card.set_toggle(options['value'])
                card.target_atrb = options['target_atrb']
            elif options['type'] == LayoutType.LayoutText.value:
                card = SettingsTextCard(key, options['value'], self.card_width)
            elif options['type'] == LayoutType.LayoutOption.value:
                card = SettingsOptionCard(key, options['options'], self.card_width, restart=False)
                card.target_atrb = options['target_atrb']
            elif options['type'] == LayoutType.LayoutOptionRestartRequired.value:
                card = SettingsOptionCard(key, options['options'], self.card_width, restart=True)
                card.target_atrb = options['target_atrb']

            if card is not None:
                self.settings_cards.append([card, options['type']])

    def set_start_position(self, factor: int) -> None:
        factor *= 30
        new_start_position = self.start_position + factor
    
        # Calculate the total height of all cards
        total_cards_height = 80 + len(self.settings_cards) * 65
    
        # Prevent further upward scrolling if the bottom card's position is less than or equal to the screen height
        if new_start_position > 20:
            self.start_position = 20
        elif total_cards_height <= self.screen.get_height() and factor < 0:
            return
        elif total_cards_height > self.screen.get_height() and new_start_position < self.screen.get_height() - total_cards_height:
            self.start_position = self.screen.get_height() - total_cards_height
        else:
            self.start_position = new_start_position

        # Update scroll bar position
        scroll_factor = (self.start_position - 20) / (self.screen.get_height() - total_cards_height)
        self.scroll_bar.set_position(self.scroll_bar.y + scroll_factor * (self.scroll_bar.height - self.scroll_bar.scroll_height))

    def update_start_position(self, scroll_factor: float) -> None:
        total_cards_height = 80 + len(self.settings_cards) * 65
        self.start_position = 20 + scroll_factor * (self.screen.get_height() - total_cards_height - 20)

    def _back_btn_fnc(self) -> None:
        if self.navigation_in_progress:
            return
        self.navigation_in_progress = True

        try:
            move = layout_manager.move_to_parent_layout()
            self._reset_start_position()
            if not move:
                if game_state.board_settings_button_pressed:
                    self.screen_manager.set_screen("board_page")
                    game_state.board_settings_button_pressed = False
                    time.sleep(0.1)
                else:
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
        temp_bottom = 0
        for i, [card, card_type] in enumerate(self.settings_cards):
            card.set_position(self.card_padding, self.start_position + 80 + i * 65)
            card.display(self.screen)

            if card_type == LayoutType.LayoutCategory.value:
                clicked = card.on_click(event, layout_manager)
                if clicked:
                    self._init_layout()
            elif card_type == LayoutType.LayoutToggle.value:
                card.on_click(event)
            elif card_type == LayoutType.LayoutOption.value or card_type == LayoutType.LayoutOptionRestartRequired.value:
                card.on_click(event)
            
            

            # Update the bottom card's position
            temp_bottom = card.bottom_pos()
        
        self.bottom_card_position = temp_bottom

        # Calculate the total height of all cards
        total_cards_height = 80 + len(self.settings_cards) * 65

        # Display the scroll bar if there are items to scroll
        if total_cards_height > self.screen.get_height():
            self.scroll_bar.display()
            self.scroll_bar.on_click(event)

        pygame.display.update()