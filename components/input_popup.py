import pygame
from states.gamestate import game_state


class InputPopup:
    def __init__(self, screen, prompt="Enter Code:", size=(360, 160), on_submit=None, on_cancel=None):
        self.screen = screen
        self.prompt = prompt
        self.size = size
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        self.popup_rect = pygame.Rect(
            (screen.get_width() - self.size[0]) // 2,
            (screen.get_height() - self.size[1]) // 2,
            self.size[0],
            self.size[1]
        )
        self.input_text = ""
        self.visible = False
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        self.input_rect = pygame.Rect(0, 0, self.size[0] - 40, 36)
        self.input_rect.center = (self.popup_rect.centerx, self.popup_rect.centery)
        self.ok_button = pygame.Rect(0, 0, 80, 36)
        self.ok_button.center = (self.popup_rect.centerx - 60, self.popup_rect.bottom - 30)
        self.cancel_button = pygame.Rect(0, 0, 80, 36)
        self.cancel_button.center = (self.popup_rect.centerx + 60, self.popup_rect.bottom - 30)

    def show(self):
        game_state.pop_up_on = True
        self.visible = True

    def hide(self):
        self.visible = False
        game_state.pop_up_on = False

    def draw(self):
        if not self.visible:
            return
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, (30, 30, 30), self.popup_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.popup_rect, 2)

        prompt_surf = self.font.render(self.prompt, True, (255, 255, 255))
        self.screen.blit(prompt_surf, (self.popup_rect.left + 20, self.popup_rect.top + 16))

        pygame.draw.rect(self.screen, (255, 255, 255), self.input_rect, 2)
        text_surf = self.font.render(self.input_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(midleft=(self.input_rect.left + 8, self.input_rect.centery))
        self.screen.blit(text_surf, text_rect)

        for rect, label in [(self.ok_button, "OK"), (self.cancel_button, "Cancel")]:
            pygame.draw.rect(self.screen, (255, 255, 255), rect)
            label_surf = self.small_font.render(label, True, (0, 0, 0))
            label_rect = label_surf.get_rect(center=rect.center)
            self.screen.blit(label_surf, label_rect)

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.ok_button.collidepoint(event.pos):
                code = self.input_text.strip().upper()
                if self.on_submit:
                    self.on_submit(code)
                self.hide()
                return True
            if self.cancel_button.collidepoint(event.pos):
                if self.on_cancel:
                    self.on_cancel()
                self.hide()
                return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                code = self.input_text.strip().upper()
                if self.on_submit:
                    self.on_submit(code)
                self.hide()
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
                return True
            else:
                ch = event.unicode
                if ch and ch.isprintable():
                    self.input_text += ch
                    return True
        return True
