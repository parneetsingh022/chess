import pygame
from utils.resource_path import resource_path

pygame.font.init()

_default_font_file = resource_path('assets/fonts/OpenSans.ttf')


DEFAULT_FONT = pygame.font.Font(_default_font_file, 26)


#SETTINGS
SETTINGS_HEADING = pygame.font.Font(_default_font_file, 30)
SETTING_FONT_CARD_HEADING = pygame.font.Font(_default_font_file, 19)
SETTINGS_FONT_VERSION = pygame.font.Font(_default_font_file, 18)
SETTING_FONT_CARD_SUBTEXT = pygame.font.Font(_default_font_file, 18)
CHEVRON_RIGHT = pygame.font.Font(_default_font_file, 35)


#GAME BOARD
CHECK_MATETEXT_MAIN = pygame.font.Font(_default_font_file, 60)