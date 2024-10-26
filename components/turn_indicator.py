import pygame
from constants import colors

class TurnIndicator:
    def __init__(self, width, height):
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.color = colors.MOVEMENT_INDICATOR_COLOR

    def set_position(self, x, y, center=False):
        if center:
            self.rect.center = (x, y)
        else:
            self.rect.topleft = (x, y)

    def display(self, screen):
        self.image.fill(self.color)
        screen.blit(self.image, self.rect)