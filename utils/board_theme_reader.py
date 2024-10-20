import os
import ast

class ThemeReader:
    def __init__(self, theme_folder="themes",  theme_file="default.th"):
        theme_file_path = os.path.join(theme_folder, theme_file)
        with open(theme_file_path, "r") as file:
            self.theme_data_raw = file.read()
        
        self.theme_data = {}

        for line in self.theme_data_raw.split("\n"):
            if line:
                key, value = line.split("=")
                try:
                    value = ast.literal_eval(value)
                except ValueError:
                    pass

                self.theme_data[key] = value

    def get_white_color(self):
        return self.theme_data["WHITE_COLOR"]
    
    def get_black_color(self):
        return self.theme_data["BLACK_COLOR"]
