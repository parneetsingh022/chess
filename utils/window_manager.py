import pygame
from utils.local_storage.storage import settings_file_manager
from typing import Callable, Optional

class WindowManager:
    def __init__(self, board_top_bar_height: int = 50):
        self.board_top_bar_height = board_top_bar_height
        self.screen = None
        self.screen_manager = None
        self.last_window_size = None
        
        # Size constants
        self.SIZE_SMALL = (450, 450 + board_top_bar_height)
        self.SIZE_MEDIUM = (650, 650 + board_top_bar_height)
        self.SIZE_LARGE = (850, 850 + board_top_bar_height)
        
        # Callback for when window is resized
        self.on_resize_callback: Optional[Callable] = None
    
    def get_size_from_setting(self, setting_value: str) -> tuple:
        """Convert setting string to size tuple"""
        if setting_value == 'small':
            return self.SIZE_SMALL
        elif setting_value == 'large':
            return self.SIZE_LARGE
        else:  # default to medium
            return self.SIZE_MEDIUM
    
    def initialize_screen(self):
        """Initialize the screen with the current settings"""
        size_setting = settings_file_manager.get_setting('win_size')
        if size_setting is None:
            size_setting = 'medium'
            settings_file_manager.save_setting('win_size', size_setting)
        
        current_size = self.get_size_from_setting(size_setting)
        self.screen = pygame.display.set_mode(current_size, pygame.DOUBLEBUF)
        self.last_window_size = size_setting
        return self.screen
    
    def set_screen_manager(self, screen_manager):
        """Set reference to screen manager for updating screens"""
        self.screen_manager = screen_manager
    
    def set_resize_callback(self, callback: Callable):
        """Set callback function to call when window is resized"""
        self.on_resize_callback = callback
    
    def check_and_apply_size_change(self):
        """Check if window size setting changed and apply it instantly"""
        current_setting = settings_file_manager.get_setting('win_size')
        
        if current_setting != self.last_window_size:
            # Setting has changed, resize the window
            new_size = self.get_size_from_setting(current_setting)
            self.screen = pygame.display.set_mode(new_size, pygame.DOUBLEBUF)
            self.last_window_size = current_setting
            
            # Update screen reference in screen manager
            if self.screen_manager:
                self.screen_manager.update_screen_reference(self.screen)
            
            # Call resize callback if set
            if self.on_resize_callback:
                self.on_resize_callback(new_size)
            
            return True
        return False

# Global instance
window_manager = WindowManager()
