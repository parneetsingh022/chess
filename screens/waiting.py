import pygame
from constants import colors
from components.buttons.button import Button
from utils.network.lan import advertise_tick
from states.gamestate import game_state


class WaitingPage:
    def __init__(self, screen: pygame.Surface, screen_manager):
        self.screen = screen
        self.screen_manager = screen_manager
        self.font_big = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 28)
        self.cancel_button = Button("Cancel")
        self.cancel_button.set_position(self.screen.get_width() // 2, self.screen.get_height() - 60, center=True)

    def display(self, event: pygame.event.Event) -> None:
        self.screen.fill(colors.BACKGROUND_COLOR)

        title = self.font_big.render("Waiting Room", True, (255, 255, 255))
        tip = self.font.render("Share this code with your friend to join:", True, (200, 200, 200))
        code = self.font_big.render(game_state.room_code or "------", True, (255, 255, 0))
        hint = self.font.render("If prompted, allow network access in Windows Firewall.", True, (180, 180, 180))

        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 80))
        self.screen.blit(tip, (self.screen.get_width() // 2 - tip.get_width() // 2, 160))
        self.screen.blit(code, (self.screen.get_width() // 2 - code.get_width() // 2, 200))
        self.screen.blit(hint, (self.screen.get_width() // 2 - hint.get_width() // 2, 260))

        # Tick advertise while on this screen
        if game_state.advertise_socket and game_state.room_code:
            advertise_tick(game_state.advertise_socket, game_state.room_code)

        self.cancel_button.display(self.screen)
        if event:
            self.cancel_button.on_click(event, self._cancel)

        pygame.display.update()

    def _cancel(self):
        # Stop hosting and return to menu
        try:
            if getattr(game_state, 'host_stop_event', None):
                try:
                    game_state.host_stop_event.set()
                except Exception:
                    pass
            if game_state.advertise_socket:
                game_state.advertise_socket.close()
        except Exception:
            pass
        game_state.multiplayer = False
        game_state.room_code = None
        game_state.is_host = False
        game_state.advertise_socket = None
        game_state.host_stop_event = None
        self.screen_manager.set_screen("menu")

    def update_screen_reference(self, new_screen):
        """Update screen reference when window is resized"""
        self.screen = new_screen
