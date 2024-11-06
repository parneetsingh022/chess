from enum import Enum

class LayoutType(Enum):
    LayoutCategory = "category"
    LayoutToggle = "toggle"
    LayoutText = "text"

class Layout:
    def __init__(self, name, layout_type: LayoutType, parent=None):
        self.name = name
        self.layout_type = layout_type
        self.sub_layouts = {}
        self.parent = parent

    def add_sub_layout(self, name, layout_type: LayoutType):
        sub_layout = Layout(name, layout_type, parent=self)
        self.sub_layouts[name] = sub_layout
        return sub_layout

    def get_layout(self):
        layout = {
            'type': self.layout_type.value,
            'sub_layout': {name: sub_layout.get_layout() for name, sub_layout in self.sub_layouts.items()}
        }
        return layout

class LayoutManager:
    def __init__(self, root_layout: Layout):
        self.current_layout = root_layout

    def move_to_sub_layout(self, name: str):
        if name in self.current_layout.sub_layouts:
            self.current_layout = self.current_layout.sub_layouts[name]
        else:
            raise ValueError(f"Sub-layout '{name}' does not exist.")

    def move_to_parent_layout(self):
        if self.current_layout.parent is None: # Already at root layout
            return False
        
        if self.current_layout.parent is not None:
            self.current_layout = self.current_layout.parent
        else:
            raise ValueError("Current layout has no parent.")
        
        return True

    def get_current_layout(self):
        return self.current_layout.get_layout()

# Example usage
root_layout = Layout(None, LayoutType.LayoutCategory)

display_settings = root_layout.add_sub_layout('Display Settings', LayoutType.LayoutCategory)
display_settings.add_sub_layout('BRIGHTNESS', LayoutType.LayoutToggle)
display_settings.add_sub_layout('RESOLUTION', LayoutType.LayoutToggle)
display_settings.add_sub_layout('ORIENTATION', LayoutType.LayoutToggle)

root_layout.add_sub_layout('Theme', LayoutType.LayoutCategory)
root_layout.add_sub_layout('Version', LayoutType.LayoutToggle)


layout_manager = LayoutManager(root_layout)

# # Move to DISPLAY SETTINGS
# layout_manager.move_to_sub_layout('DISPLAY SETTINGS')
# print(layout_manager.get_current_layout())

# # Move back to ROOT
# layout_manager.move_to_parent_layout(root_layout)
# print(layout_manager.get_current_layout())