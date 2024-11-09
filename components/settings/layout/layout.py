from enum import Enum

class LayoutType(Enum):
    LayoutCategory = "category"
    LayoutToggle = "toggle"
    LayoutText = "text"

class Layout:
    def __init__(self, name, layout_type: LayoutType, parent=None, target_atrb=None):
        self.name = name
        self.layout_type = layout_type
        self.sub_layouts = {}
        self.parent = parent
        self.target_atrb = target_atrb

    def add_sub_layout(self, name, layout_type: LayoutType, target_atrb=None):
        sub_layout = Layout(name, layout_type, parent=self, target_atrb=target_atrb)
        self.sub_layouts[name] = sub_layout
        return sub_layout

    def get_layout(self):
        layout = {
            'type': self.layout_type.value,
            'sub_layout': {name: sub_layout.get_layout() for name, sub_layout in self.sub_layouts.items()},
            'target_atrb': self.target_atrb
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
        if self.current_layout.parent is None:  # Already at root layout
            return False
        
        if self.current_layout.parent is not None:
            self.current_layout = self.current_layout.parent
        else:
            raise ValueError("Current layout has no parent.")
        
        return True

    def get_current_layout(self):
        return self.current_layout.get_layout()

# Example usage
root_layout = Layout('ROOT', LayoutType.LayoutCategory)

general = root_layout.add_sub_layout('General', LayoutType.LayoutCategory)
general.add_sub_layout('Movement Indicators', LayoutType.LayoutToggle, target_atrb='movement_indicators')
general.add_sub_layout('Show turn indicator', LayoutType.LayoutToggle, target_atrb='turn_indicator')

root_layout.add_sub_layout('Theme', LayoutType.LayoutCategory)
root_layout.add_sub_layout('Version', LayoutType.LayoutToggle)

layout_manager = LayoutManager(root_layout)