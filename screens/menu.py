from constants import colors
import pygame
from components.buttons.button import Button
from utils.screen_manager import ScreenManager
from utils.resource_path import resource_path
from states.gamestate import game_state
import os
from utils.local_storage.storage import settings_file_manager

def quit_button_action():
    pygame.quit()
    quit()

def start_new(screen_manager: ScreenManager):
    # Ensure any multiplayer state is cleared when starting a solo game
    try:
        if game_state.net_socket:
            try:
                game_state.net_socket.close()
            except Exception:
                pass
        if game_state.advertise_socket:
            try:
                game_state.advertise_socket.close()
            except Exception:
                pass
    finally:
        game_state.multiplayer = False
        game_state.room_code = None
        game_state.is_host = False
        game_state.net_socket = None
        game_state.advertise_socket = None
        game_state.my_color = None
    game_state.start_new = True
    game_state.in_game = False
    screen_manager.set_screen("board_page")

def resume_game(screen_manager: ScreenManager):
    screen_manager.set_screen("board_page")

class MenuPage:
    def __init__(self, screen: pygame.Surface, screen_manager: ScreenManager):
        self.screen = screen
        self.screen_manager = screen_manager
        self.is_resume_added = False

        # All main-menu buttons with borders enabled
        self.start_button       = Button("Start",       border=True)
        self.start_new_game     = Button("New Game",    border=True)
        self.resume_button      = Button("Resume",      border=True)
        self.settings_button    = Button("Settings",    border=True)
        self.quit_button        = Button("Quit",        border=True)
        self.multiplayer_button = Button("Multiplayer", border=True)

        # Pair buttons with their callbacks
        self.start_button_item          = (self.start_button,       lambda: resume_game(self.screen_manager))
        self.start_new_game_button_item = (self.start_new_game,     lambda: start_new(self.screen_manager))
        self.resume_button_item         = (self.resume_button,      lambda: resume_game(self.screen_manager))
        self.settings_button_item       = (self.settings_button,    lambda: self.screen_manager.set_screen("settings"))
        self.quit_button_item           = (self.quit_button,        quit_button_action)
        self.multiplayer_button_item    = (self.multiplayer_button, lambda: self.screen_manager.set_screen("multiplayer"))

        self.button_padding = 20
        # Initial menu order (before checking in-game state)
        self.menu_buttons = [
            self.start_button_item,
            self.multiplayer_button_item,
            self.settings_button_item,
            self.quit_button_item,
        ]

        # Version label font (if you need to display version)
        self.font = pygame.font.Font(None, 25)

        # Load and prepare logo
        logo_path = resource_path(os.path.join("assets", "icon.png"))
        self.logo_image = pygame.image.load(logo_path).convert_alpha()
        self.cur_size = settings_file_manager.get_setting("win_size")

    def display(self, event: pygame.event.Event) -> None:
        # Clear background
        self.screen.fill(colors.BACKGROUND_COLOR)

        # Scale logo based on window size
        if self.cur_size == "small":
            self.logo_image = pygame.transform.smoothscale(self.logo_image, (200, 200))
        else:
            self.logo_image = pygame.transform.smoothscale(self.logo_image, (400, 400))

        # Switch between Start/Resume + New Game depending on game state
        if game_state.in_game and not self.is_resume_added:
            self.menu_buttons.pop(0)
            self.menu_buttons.insert(0, self.resume_button_item)
            self.menu_buttons.insert(1, self.start_new_game_button_item)
            self.is_resume_added = True
        elif not game_state.in_game and self.is_resume_added:
            # Remove Resume and New Game
            self.menu_buttons.pop(0)
            self.menu_buttons.pop(0)
            self.menu_buttons.insert(0, self.start_button_item)
            self.is_resume_added = False

        # ── Enforce uniform button width ─────────────────────────
        max_width = max(btn.button_rect.width for btn, _ in self.menu_buttons)
        max_width = max(max_width, 200)  # Ensure at least 200px width
        for btn, _ in self.menu_buttons:
            btn.button_rect.width = max_width
            btn.text_rect.center = btn.button_rect.center
        # ───────────────────────────────────────────────────────────

        # Compute vertical layout
        total_menu_height = sum(
            btn.get_button_height() + self.button_padding
            for btn, _ in self.menu_buttons
        )
        start_y = (self.screen.get_height() - total_menu_height) // 2

        # ── Dynamically center horizontally to the right of logo ──
        logo_w     = self.logo_image.get_width()
        available_w = self.screen.get_width() - logo_w
        x_center    = logo_w + available_w // 2
        # ───────────────────────────────────────────────────────────

        # Place each button
        cur_y = start_y
        for btn, _ in self.menu_buttons:
            btn.set_position(x_center-20, cur_y, center=True)
            cur_y += btn.get_button_height() + self.button_padding

        # Draw buttons and handle clicks
        for btn, action in self.menu_buttons:
            btn.display(self.screen)
            btn.on_click(event, action)

        # Draw logo vertically centered next to the menu
        first_y  = self.menu_buttons[0][0].get_start_position()[1]
        last_y   = self.menu_buttons[-1][0].get_end_position()[1]
        mid_y    = (first_y + last_y) // 2
        logo_h   = self.logo_image.get_height()
        self.screen.blit(self.logo_image, (-10, mid_y - logo_h // 2 + 10))

        pygame.display.update()
