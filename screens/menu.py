from constants import colors
import pygame
from components.buttons.button import Button
from utils.screen_manager import ScreenManager
from utils.resource_path import resource_path
from states.gamestate import game_state
import os
from utils.local_storage.storage import settings_file_manager  # Import the SettingsFileManager class
from components.input_popup import InputPopup
from utils.network.code import generate_room_code
from utils.network.lan import host_advertise, host_wait_for_connection, client_find_host, client_connect, advertise_tick
import threading

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
        self.is_resume_added = False
        self.screen_manager = screen_manager

        self.start_button = Button("Start")
        self.start_new_game = Button("New Game")
        self.resume_button = Button("Resume")
        self.settings_button = Button("Settings")
        self.quit_button = Button("Quit")
        self.host_button = Button("Host (LAN)")
        self.join_button = Button("Join (LAN)")

        self.start_button_item = (self.start_button, lambda: resume_game(screen_manager))
        self.resume_button_item = (self.resume_button, lambda: resume_game(self.screen_manager))
        self.start_new_game_button_item = (self.start_new_game, lambda: start_new(self.screen_manager))
        self.settings_button_item = (self.settings_button, lambda: screen_manager.set_screen("settings"))
        self.quit_button_item = (self.quit_button, quit_button_action)
        self.host_button_item = (self.host_button, self._host_game)
        self.join_button_item = (self.join_button, self._join_game)

        self.button_padding = 20
        self.menu_buttons = [
            self.start_button_item,
            self.host_button_item,
            self.join_button_item,
            self.settings_button_item,
            self.quit_button_item,
        ]
        self.input_popup = None
        # Initialize font for version label
        self.font = pygame.font.Font(None, 25)  # You can specify a font file and size

        self.logo_image = pygame.image.load(resource_path(os.path.join("assets", "icon.png")))
        self.logo_image = self.logo_image.convert_alpha()
        self.cur_size = settings_file_manager.get_setting("win_size")

    def display(self, event: pygame.event.Event) -> None:
        
        self.screen.fill(colors.BACKGROUND_COLOR)

        if self.cur_size == "small":
            self.logo_image = pygame.transform.smoothscale(self.logo_image, (200, 200))
        else:
            self.logo_image = pygame.transform.smoothscale(self.logo_image, (400, 400))

        if game_state.in_game and not self.is_resume_added:
            self.menu_buttons.pop(0)
            self.menu_buttons.insert(
                0, self.resume_button_item
            )

            self.menu_buttons.insert(
                1, self.start_new_game_button_item
            )
            
            
            self.is_resume_added = True

        elif not game_state.in_game and self.is_resume_added:
            self.menu_buttons.pop(0)  # Remove "Resume" button
            self.menu_buttons.pop(0)  # Remove "New Game" button
            self.menu_buttons.insert(0, self.start_button_item)
            self.is_resume_added = False
            

        # Calculate the total height of the menu
        total_menu_height = 0
        for button, _ in self.menu_buttons:
            total_menu_height += button.get_button_height() + self.button_padding

        # Calculate the starting height of the menu
        start_height = (
            self.screen.get_height() - total_menu_height
        ) // 2

        # Display the menu buttons on the screen
        del_y = 0
        for button, _ in self.menu_buttons:
            offset = 100
            if self.cur_size == "small":
                offset = 150
            elif self.cur_size == "large":
                offset = 200
            button.set_position(self.logo_image.get_rect().bottomright[0]+offset, start_height + del_y, center=True)
            del_y += button.get_button_height() + self.button_padding

        # Display the menu buttons on the screen
        for button, action in self.menu_buttons:
            button.display(self.screen)
            button.on_click(event, action)

        # Tick advertise if hosting
        if game_state.multiplayer and game_state.is_host and game_state.advertise_socket and game_state.room_code:
            advertise_tick(game_state.advertise_socket, game_state.room_code)
            # Draw a visible banner with the room code while waiting
            banner_text1 = self.font.render(f"Hosting LAN game", True, (255, 255, 255))
            banner_text2 = self.font.render(f"Code: {game_state.room_code}", True, (255, 255, 0))
            banner_text3 = self.font.render("Waiting for player to join…", True, (200, 200, 200))
            tip_text = self.font.render("If prompted, allow network access in Windows Firewall.", True, (180, 180, 180))
            bx = 20
            by = self.screen.get_height() - 100
            self.screen.blit(banner_text1, (bx, by))
            self.screen.blit(banner_text2, (bx, by + 22))
            self.screen.blit(banner_text3, (bx, by + 44))
            self.screen.blit(tip_text, (bx, by + 66))
    
        start_y = self.menu_buttons[0][0].get_start_position()[1]
        end_y = self.menu_buttons[-1][0].get_end_position()[1]
        middle_y = (start_y + end_y) // 2
        logo_height = self.logo_image.get_height()
        logo_start = (middle_y - logo_height // 2)
        self.screen.blit(self.logo_image, (0, logo_start+10))

        # Draw input popup if present
        if self.input_popup:
            self.input_popup.draw()

        pygame.display.update()

        # Handle popup events
        if self.input_popup and event:
            if self.input_popup.handle_event(event):
                return

    def _host_game(self):
        if game_state.in_game:
            return
        code = generate_room_code()
        game_state.multiplayer = True
        game_state.is_host = True
        game_state.room_code = code
        game_state.advertise_socket = host_advertise(code)
        print(f"[LAN] Hosting game. Room code: {code}")

        def accept_thread():
            conn, _ = host_wait_for_connection(code)
            game_state.net_socket = conn
            try:
                game_state.net_socket.setblocking(False)
            except Exception:
                pass
            game_state.my_color = 'white'
            # Start game when client connects
            self._start_multiplayer_game(host=True)

        threading.Thread(target=accept_thread, daemon=True).start()

    def _join_game(self):
        if game_state.in_game:
            return
        # Show input popup for code entry
        self.input_popup = InputPopup(self.screen, prompt="Enter Room Code:", on_submit=self._join_with_code, on_cancel=self._cancel_join)
        self.input_popup.show()

    def _cancel_join(self):
        self.input_popup = None

    def _join_with_code(self, code: str):
        self.input_popup = None
        found = client_find_host(timeout=1.5)
        if not found:
            return
        ip, port, ad_code = found
        if ad_code != code:
            return
        sock = client_connect(ip, port, code)
        if sock is None:
            return
        game_state.multiplayer = True
        game_state.is_host = False
        game_state.room_code = code
        game_state.net_socket = sock
        try:
            game_state.net_socket.setblocking(False)
        except Exception:
            pass
        game_state.my_color = 'black'
        self._start_multiplayer_game(host=False)

    def _start_multiplayer_game(self, host: bool):
        # Host plays white by default
        game_state.start_new = True
        game_state.in_game = False
        self.screen_manager.set_screen("board_page")