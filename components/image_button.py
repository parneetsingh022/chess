import pygame
from utils.resource_path import resource_path

class ImageButton:
    def __init__(self, image_path: str, width: int, height: int):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.on_click_action = None

    def set_position(self, x: int, y: int):
        self.rect.topleft = (x, y)

    def display(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)

    def on_click(self, event: pygame.event.Event, action):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            if self.rect.collidepoint(event.pos):
                if action:
                    action()
    # returns the end position of the button/image
    def end_pos(self) -> int:
        return self.rect.right
    
    def start_pos(self) -> int:
        return self.rect.left

class BackButton(ImageButton):
    def __init__(self):
        super().__init__(resource_path("assets/icons/back_button_icon.png"), 30, 30)

class SettingsButton(ImageButton):
    def __init__(self):
        super().__init__(resource_path("assets/icons/settings_button_icon.png"), 30, 30)

class RestartButton(ImageButton):
    def __init__(self):
        super().__init__(resource_path("assets/icons/restart_button_icon.png"), 30, 30)