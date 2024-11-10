import pygame

class ToggleButton:
    def __init__(self, screen, x, y, on_image_path="assets/icons/toggle_on.png", off_image_path="assets/icons/toggle_off.png", initial_state=False, size=(50, 50)):
        self.screen = screen
        self.pos = (x, y)
        self.state = initial_state
        self.on_image = pygame.transform.scale(pygame.image.load(on_image_path), size)
        self.off_image = pygame.transform.scale(pygame.image.load(off_image_path), size)
        self.image = self.on_image if self.state else self.off_image
        self.rect = self.image.get_rect(topleft=self.pos)
        self.mouse_down = False

    def toggle(self):
        self.state = not self.state
        self.image = self.on_image if self.state else self.off_image

    def display(self):
        self.screen.blit(self.image, self.pos)

    def set_state(self, state):
        self.state = state
        self.image = self.on_image if self.state else self.off_image

    def get_state(self):
        return self.state