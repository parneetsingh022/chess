import pygame
from constants import colors, fonts
from typing import Callable, Tuple

class Button:
    def __init__(self, text: str, padding: int = 10, border=False):
        self.text_string = text
        self.font_color = colors.FONT_COLOR_BLACK
        self.border_color = colors.FONT_COLOR_BLACK
        self.font = fonts.DEFAULT_FONT
        self.padding = padding
        self.is_pressed = False
        self.border = border
        self.disable = False

        self._radius = 16

        # Hover tracking
        self._last_tick = pygame.time.get_ticks()
        self._was_hovered = False
        self._hover_started = False
        self._hover_fade_done = False

        # Ripple effect
        self._ripple_active = False
        self._ripple_center = (0, 0)
        self._ripple_radius = 0.0
        self._ripple_max_radius = 0.0
        self._ripple_duration = 0.8  # seconds for ripple to expand
        self._ripple_speed = 0.0     # will be computed on start
        self._max_alpha = 80         # peak alpha of ripple

        self.update_text(text)

    def update_text(self, text: str):
        self.text_string = text
        self.text = self.font.render(text, True, self.font_color)
        self.text_rect = self.text.get_rect()

        if self.border:
            self.button_rect = self.text_rect.inflate(2 * self.padding, 2 * self.padding)
            self.text_rect.center = self.button_rect.center
        else:
            self.button_rect = self.text_rect

    def set_position(self, x: int, y: int, center: bool = False):
        if center:
            self.button_rect.center = (x, y)
        else:
            self.button_rect.topleft = (x, y)
        self.text_rect.center = self.button_rect.center

    def display(self, screen: pygame.Surface):
        now = pygame.time.get_ticks()
        dt = (now - self._last_tick) / 1000.0
        self._last_tick = now

        mouse_pos = pygame.mouse.get_pos()
        hovered = self.button_rect.collidepoint(mouse_pos) and not self.disable

        # Hover enter
        if hovered and not self._was_hovered:
            self._hover_started = True
            self._hover_fade_done = False
            if self.border:
                self._start_ripple(mouse_pos)

        # Hover exit
        if not hovered and self._was_hovered:
            self._hover_started = False
            self._hover_fade_done = False

        self._was_hovered = hovered

        # Draw button background & border
        if self.border:
            self._draw_button(screen)

        # Draw text
        screen.blit(self.text, self.text_rect)

        # Draw ripple on top
        if self.border and self._ripple_active:
            self._draw_ripple(screen, dt)

    def _draw_button(self, screen: pygame.Surface):
        rect = self.button_rect
        if self._hover_started and not self._hover_fade_done:
            bg_color = (230, 230, 255)
        else:
            bg_color = (255, 255, 255)
        pygame.draw.rect(screen, bg_color, rect, border_radius=self._radius)
        border_color = (180, 200, 255) if self._hover_started else (240, 240, 240)
        pygame.draw.rect(screen, border_color, rect, width=1, border_radius=self._radius)

    def _start_ripple(self, mouse_pos: Tuple[int, int]):
        self._ripple_active = True
        self._ripple_center = mouse_pos
        self._ripple_radius = 0.0

        dx = max(abs(mouse_pos[0] - self.button_rect.left),
                 abs(mouse_pos[0] - self.button_rect.right))
        dy = max(abs(mouse_pos[1] - self.button_rect.top),
                 abs(mouse_pos[1] - self.button_rect.bottom))
        self._ripple_max_radius = (dx**2 + dy**2) ** 0.5

        # compute speed so it finishes in _ripple_duration
        self._ripple_speed = self._ripple_max_radius / self._ripple_duration

    def _draw_ripple(self, screen: pygame.Surface, dt: float):
        # advance radius by dt-based speed
        self._ripple_radius += dt * self._ripple_speed

        # finish ripple when max reached
        if self._ripple_radius >= self._ripple_max_radius:
            self._ripple_active = False
            self._hover_fade_done = True
            return

        progress = self._ripple_radius / self._ripple_max_radius
        ripple_alpha = int(self._max_alpha * (1 - progress**2))
        if ripple_alpha <= 0:
            self._ripple_active = False
            self._hover_fade_done = True
            return

        # draw on temporary surface
        w, h = self.button_rect.size
        ripple_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        local_center = (self._ripple_center[0] - self.button_rect.x,
                        self._ripple_center[1] - self.button_rect.y)
        pygame.draw.circle(ripple_surf,
                           (120, 180, 255, ripple_alpha),
                           local_center,
                           int(self._ripple_radius))

        # mask to keep ripple within rounded rect
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=self._radius)
        ripple_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        screen.blit(ripple_surf, self.button_rect.topleft, special_flags=pygame.BLEND_PREMULTIPLIED)

    def clear(self, screen: pygame.Surface, background_color: tuple = colors.BACKGROUND_COLOR):
        pygame.draw.rect(screen, background_color, self.button_rect)

    def on_click(self, event: pygame.event.Event, fnc: Callable[[], None]) -> bool:
        if self.disable or event is None:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and self.button_rect.collidepoint(event.pos):
            self.is_pressed = True
            if self.border:
                self._start_ripple(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and self.is_pressed:
            if self.button_rect.collidepoint(event.pos):
                fnc()
            self.is_pressed = False
            return True
        return False

    def disable_button(self):
        self.disable = True
        self.font_color = colors.FONT_COLOR_GREY
        self.border_color = colors.FONT_COLOR_GREY
        self.update_text(self.text_string)

    def get_button_height(self):
        return self.button_rect.height

    def get_start_position(self):
        return self.button_rect.topleft

    def get_end_position(self):
        return self.button_rect.bottomright
