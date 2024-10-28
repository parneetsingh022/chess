class ScreenManager:
    def __init__(self, screen):
        self.screen = screen
        self.screens = {}
        self.current_screen = None
        self.current_screen_name = None

    def add_screen(self, name, screen):
        self.screens[name] = screen

    def set_screen(self, name):
        self.current_screen = self.screens.get(name)
        self.current_screen_name = name

    def display_current_screen(self, event):
        if self.current_screen:
            self.current_screen.display(event)

    def get_screen(self):
        return self.current_screen_name