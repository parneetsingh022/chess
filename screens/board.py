from constants import colors, fonts
import pygame

from utils.screen_manager import ScreenManager

class BoardPage:
    def __init__(self, screen: pygame.Surface, screen_manager : ScreenManager):
        self.screen = screen
        self.font = fonts.DEFAULT_FONT  # Use the default font from your constants
        self.label_text = "BoardPage"
        self.label_color = colors.FONT_COLOR_BLACK  # Use a color from your constants

    def display(self, event: pygame.event.Event) -> None:
        self.screen.fill(colors.BACKGROUND_COLOR)

        # Render the label text
        label = self.font.render(self.label_text, True, self.label_color)
        label_rect = label.get_rect(center=(self.screen.get_width() // 2, 50))  # Position at the top center

        # Blit the label onto the screen
        self.screen.blit(label, label_rect)

        pygame.display.update()