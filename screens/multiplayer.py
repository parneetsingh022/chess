import pygame
import threading
from constants import colors
from components.buttons.button import Button
from components.input_popup import InputPopup
from states.gamestate import game_state
from utils.network.code import generate_room_code
from utils.network.lan import host_advertise, host_wait_for_connection, client_find_host, client_connect


class MultiplayerPage:
    def __init__(self, screen: pygame.Surface, screen_manager):
        self.screen = screen
        self.screen_manager = screen_manager
        self.title_font = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 28)

        self.host_button = Button("Host Game")
        self.join_button = Button("Join Game")
        self.back_button = Button("Back")

        self.input_popup = None

    def display(self, event: pygame.event.Event) -> None:
        self.screen.fill(colors.BACKGROUND_COLOR)

        title = self.title_font.render("Multiplayer", True, (255, 255, 255))
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 100))

        # Layout buttons
        cx = self.screen.get_width() // 2
        self.host_button.set_position(cx, 200, center=True)
        self.join_button.set_position(cx, 250, center=True)
        self.back_button.set_position(cx, 320, center=True)

        for btn, action in [
            (self.host_button, self._host_game),
            (self.join_button, self._join_game),
            (self.back_button, lambda: self.screen_manager.set_screen("menu")),
        ]:
            btn.display(self.screen)
            btn.on_click(event, action)

        # Draw and handle input popup
        if self.input_popup:
            self.input_popup.draw()
            if event and self.input_popup.handle_event(event):
                return
        pygame.display.update()

    def _host_game(self):
        if game_state.in_game:
            return
        code = generate_room_code()
        game_state.multiplayer = True
        game_state.is_host = True
        game_state.room_code = code
        game_state.advertise_socket = host_advertise(code)

        def accept_thread():
            result = host_wait_for_connection(code)
            if isinstance(result, tuple) and len(result) == 3:
                conn, _, host_color = result
            else:
                conn, _ = result
                host_color = 'white'
            game_state.net_socket = conn
            try:
                game_state.net_socket.setblocking(False)
            except Exception:
                pass
            game_state.my_color = host_color
            # Start game when client connects
            self._start_game()

        threading.Thread(target=accept_thread, daemon=True).start()
        # Navigate to the waiting room
        self.screen_manager.set_screen("waiting")

    def _join_game(self):
        if game_state.in_game:
            return
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
        result = client_connect(ip, port, code)
        if result is None:
            return
        if isinstance(result, tuple):
            sock, your_color = result
        else:
            sock = result
            your_color = 'black'
        game_state.multiplayer = True
        game_state.is_host = False
        game_state.room_code = code
        game_state.net_socket = sock
        try:
            game_state.net_socket.setblocking(False)
        except Exception:
            pass
        game_state.my_color = your_color or 'black'
        self._start_game()

    def _start_game(self):
        game_state.start_new = True
        game_state.in_game = False
        self.screen_manager.set_screen("board_page")
