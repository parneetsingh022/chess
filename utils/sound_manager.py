import os
import pygame
from typing import Optional
from utils.resource_path import resource_path


class SoundManager:
    def __init__(self):
        self._ready = False
        self._move: Optional[pygame.mixer.Sound] = None
        self._capture: Optional[pygame.mixer.Sound] = None
        self._check: Optional[pygame.mixer.Sound] = None
        self._ensure_init()

    def _ensure_init(self):
        try:
            if pygame.mixer.get_init() is None:
                # Reasonable defaults; let pygame choose best driver
                pygame.mixer.init()
            # Load sounds
            self._move = self._load("assets/sounds/move-self.mp3")
            self._capture = self._load("assets/sounds/capture.mp3")
            self._check = self._load("assets/sounds/move-check.mp3")
            self._ready = True
        except Exception:
            # Audio not available or files missing; keep gracefully disabled
            self._ready = False

    def _load(self, rel_path: str) -> Optional[pygame.mixer.Sound]:
        try:
            full = resource_path(rel_path)
            if os.path.exists(full):
                return pygame.mixer.Sound(full)
        except Exception:
            pass
        return None

    def play_move(self):
        if self._ready and self._move is not None:
            self._move.play()

    def play_capture(self):
        if self._ready and self._capture is not None:
            self._capture.play()

    def play_check(self):
        if self._ready and self._check is not None:
            self._check.play()


_instance: Optional[SoundManager] = None


def get_sound_manager() -> SoundManager:
    global _instance
    if _instance is None:
        _instance = SoundManager()
    return _instance
