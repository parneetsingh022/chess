import pygame
import sys
from states.gamestate import game_state
import time

class Popup:
    def __init__(self, screen, message, button_type="ok", size=(300, 200), callbacks=None):
        self.screen = screen
        self.message = message
        self.button_type = button_type
        self.size = size
        self.font = pygame.font.SysFont(None, 36)
        self.text = self.font.render(self.message, True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center=(self.size[0] // 2, self.size[1] // 3))
        self.popup_rect = pygame.Rect(
            (screen.get_width() - self.size[0]) // 2,
            (screen.get_height() - self.size[1]) // 2,
            self.size[0],
            self.size[1]
        )
        self.callbacks = callbacks if callbacks else {}
        self.buttons = self.create_buttons()
        self.visible = False

        

    def create_buttons(self):
        buttons = []
        if self.button_type == "yesno":
            yes_button = pygame.Rect(0, 0, 80, 40)
            yes_button.center = (self.popup_rect.centerx - 50, self.popup_rect.centery + 50)
            no_button = pygame.Rect(0, 0, 80, 40)
            no_button.center = (self.popup_rect.centerx + 50, self.popup_rect.centery + 50)
            buttons.append(("Yes", yes_button, self.callbacks.get("yes")))
            buttons.append(("No", no_button, self.callbacks.get("no")))
        elif self.button_type == "ok":
            ok_button = pygame.Rect(0, 0, 80, 40)
            ok_button.center = (self.popup_rect.centerx, self.popup_rect.centery + 50)
            buttons.append(("OK", ok_button, self.callbacks.get("ok")))
        return buttons

    def show(self):
        game_state.pop_up_on = True
        #pygame.event.post(pygame.event.Event(POPUP_EVENT_ON))
        self.visible = True

    def hide(self):
        self.visible = False
        game_state.pop_up_on = False
        #pygame.event.post(pygame.event.Event(POPUP_EVENT_CLOSE))
        

    def draw(self):
        if not self.visible:
            return

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with alpha for transparency

        self.screen.blit(overlay, (0, 0))
        self.screen.blit(self.text, self.text_rect.move(self.popup_rect.topleft))

        for text, button, _ in self.buttons:
            pygame.draw.rect(self.screen, (255, 255, 255), button)
            button_text = self.font.render(text, True, (0, 0, 0))
            button_text_rect = button_text.get_rect(center=button.center)
            self.screen.blit(button_text, button_text_rect)

    def handle_event(self, event):
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for text, button, callback in self.buttons:
                if button.collidepoint(mouse_pos):
                    if callback:
                        callback()
                    self.hide()
                    
                    return True
        return True  # Capture all events when the popup is visible