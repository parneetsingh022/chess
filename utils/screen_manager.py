class ScreenManager:
    def __init__(self, screen):
        self.screen = screen
        self.screens = {}
        self.current_screen = None

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def set_screen(self, name):
        self.current_screen = self.screens.get(name)

    def display_current_screen(self, event):
        if self.current_screen:
            self.current_screen.display(event)