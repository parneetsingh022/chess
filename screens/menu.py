from constants import colors
import pygame
from components.buttons.button import Button
from utils.screen_manager import ScreenManager
from utils.versions.version_reader import read_version_from_file

def quit_button_action():
    pygame.quit()
    quit()

class MenuPage:
    def __init__(self, screen: pygame.Surface, screen_manager: ScreenManager):
        self.screen = screen
        
        self.start_button = Button("Start")
        self.settings_button = Button("Settings")
        self.settings_button.disable_button()  # Will implement in future
        self.quit_button = Button("Quit")

        self.button_padding = 20
        self.menu_buttons = [
            (self.start_button, lambda: screen_manager.set_screen("board_page")),
            (self.settings_button, None),
            (self.quit_button, quit_button_action),
        ]

        self.release_notes_file = "release.json"
        self.version = read_version_from_file(self.release_notes_file)

        # Initialize font for version label
        self.font = pygame.font.Font(None, 25)  # You can specify a font file and size

    def display(self, event: pygame.event.Event) -> None:
        self.screen.fill(colors.BACKGROUND_COLOR)

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
        for button, action in self.menu_buttons:
            button.display(self.screen)
            button.set_position(
                self.screen.get_width() // 2, 
                start_height + del_y, 
                center=True
            )

            del_y += (
                button.get_button_height() + self.button_padding
            )
            button.on_click(event, action)

        # Render and display the version label
        version_text = self.font.render(f"Version: {self.version}", True, colors.FONT_COLOR_GREY)
        version_rect = version_text.get_rect()
        version_rect.bottomright = (self.screen.get_width() - 10, self.screen.get_height() - 10)
        self.screen.blit(version_text, version_rect)

        pygame.display.update()