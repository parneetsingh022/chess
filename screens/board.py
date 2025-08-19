from constants import colors, fonts
import random
import pygame

from utils.screen_manager import ScreenManager
from utils.chess_board_manager import ChessBoardManager
from utils.board_pieces_manager import BoardPiecesManager
from utils.arrow_manager import ArrowManager
from utils.highlight_manager import HighlightManager
from utils.local_storage.storage import settings_file_manager

from components.image_button import ImageButton, BackButton, SettingsButton, RestartButton, ResignButton
from enum import Enum
from states.gamestate import game_state

import os

# Bot profiles: adjust, add, or remove entries as needed. Each entry auto-renders in the side panel.
BOT_PROFILES = [
    {"name": "Chuck", "rating": 400, "image_path": "assets\\avatar\\chuck.png"},
    {"name": "Edith 1", "rating": 500, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Edith 2", "rating": 500, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Edith 3", "rating": 500, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Edith 4", "rating": 500, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 5", "rating": 800, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 6", "rating": 800, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 7", "rating": 800, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 8", "rating": 800, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 9", "rating": 800, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 10", "rating": 800, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 11", "rating": 1200, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 12", "rating": 1200, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 13", "rating": 1200, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 14", "rating": 1200, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 15", "rating": 1200, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 16", "rating": 1200, "image_path": "assets\\avatar\\edith.png"},
    {"name": "Amily 17", "rating": 2200, "image_path": "assets\\avatar\\edith.png"},

    {"name": "Amily 18", "rating": 3000, "image_path": "assets\\avatar\\edith.png"},
]


class SidePanel:
    """Simple side panel container to stack UI elements vertically."""
    def __init__(self, screen: pygame.Surface, top_bar_height: int, width: int):
        self.screen = screen
        self.top_bar_height = top_bar_height
        self.width = width
        self.x = 0
        self.top = top_bar_height
        self.height = 0
        self.bg_color = (30, 30, 38)
        self.padding_x = 16
        self.spacing_y = 8
        # Elements: list of tuples (kind, data)
        self.elements = []  # [(kind, surface)]
        self.bot_items = []  # each: {profile, image, rect}
        # Bot selection visuals
        self._bot_image_size = (60, 60)  # enlarged from 48 for better visibility
        self._bot_select_callback = None
        self._selected_bot_index = None  # selected index or None
        # Scrolling state
        self.scroll_offset = 0
        self.content_height = 0
        self._last_view_height = 0
        self._scroll_speed = 80  # pixels per wheel notch

    def update_geometry(self, x: int, top: int, height: int):
        self.x = x
        self.top = top
        self.height = height

    def add_text(self, text: str, size: int = 20, color=(200, 200, 200), font: pygame.font.Font | None = None):
        font_obj = font or pygame.font.Font(None, size)
        surf = font_obj.render(text, True, color)
        self.elements.append(("text", surf))

    def add_bots(self, profiles: list[dict], on_select=None):
        """Add bot selection images from list of dicts: {name, rating, image_path}."""
        self.bot_items.clear()
        self._bot_select_callback = on_select
        for p in profiles:
            img_path = p.get("image_path")
            surf = None
            if img_path and os.path.exists(img_path):
                try:
                    surf = pygame.image.load(img_path).convert_alpha()
                    surf = pygame.transform.smoothscale(surf, self._bot_image_size)
                except Exception:
                    surf = None
            if surf is None:
                # Fallback placeholder surface
                surf = pygame.Surface(self._bot_image_size, pygame.SRCALPHA)
                surf.fill((70,70,90))
                fnt = pygame.font.Font(None, 18)
                label = fnt.render("?", True, (220,220,220))
                r = label.get_rect(center=(self._bot_image_size[0]//2, self._bot_image_size[1]//2))
                surf.blit(label, r)
            self.bot_items.append({"profile": p, "image": surf, "rect": pygame.Rect(0,0,*self._bot_image_size)})

    def _category_for_rating(self, rating: int) -> str:
        if rating <= 500:
            return "Beginner"
        if rating <= 900:
            return "Easy"
        if rating <= 1500:
            return "Intermediate"
        if rating <= 2000:
            return "Hard"
        return "Advanced"

    def handle_event(self, event: pygame.event.Event):
        if event and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Skip selection if a game is running (lock during active game)
            if game_state.in_game:
                return
            pos = event.pos
            # Only allow selection if click is inside current panel rectangle
            if not (self.x <= pos[0] <= self.x + self.width and self.top <= pos[1] <= self.top + self.height):
                return
            # Iterate bot item rects
            for idx, item in enumerate(self.bot_items):
                if item["rect"].collidepoint(pos):
                    self._selected_bot_index = idx
                    if self._bot_select_callback:
                        try:
                            self._bot_select_callback(item["profile"])
                        except Exception:
                            pass
                    break
        # Mouse wheel scrolling (buttons 4 up, 5 down)
        if event and event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            # Only scroll if pointer is inside panel area
            if self.x <= event.pos[0] <= self.x + self.width and self.top <= event.pos[1] <= self.top + self.height:
                max_scroll = max(0, self.content_height - self.height)
                if event.button == 4:  # wheel up
                    self.scroll_offset = max(0, self.scroll_offset - self._scroll_speed)
                elif event.button == 5:  # wheel down
                    self.scroll_offset = min(max_scroll, self.scroll_offset + self._scroll_speed)
        # Pygame 2 MOUSEWHEEL event support
        if event and event.type == pygame.MOUSEWHEEL:
            if self.x <= pygame.mouse.get_pos()[0] <= self.x + self.width and self.top <= pygame.mouse.get_pos()[1] <= self.top + self.height:
                max_scroll = max(0, self.content_height - self.height)
                # event.y is positive when scrolled up
                self.scroll_offset -= event.y * self._scroll_speed
                if self.scroll_offset < 0:
                    self.scroll_offset = 0
                if self.scroll_offset > max_scroll:
                    self.scroll_offset = max_scroll

    def clear(self):
        self.elements.clear()

    def draw(self):
        rect = pygame.Rect(self.x, self.top, self.width, self.height)
        pygame.draw.rect(self.screen, self.bg_color, rect)
        prev_clip = self.screen.get_clip()
        self.screen.set_clip(rect)

        view_top = self.top
        view_height = self.height
        self._last_view_height = view_height
        y = self.top + 10 - self.scroll_offset

        # Static text elements
        for kind, data in self.elements:
            if kind == "text":
                surf: pygame.Surface = data  # type: ignore
                if y + surf.get_height() >= view_top and y <= view_top + view_height:
                    self.screen.blit(surf, (self.x + self.padding_x, y))
                y += surf.get_height() + self.spacing_y

        # Bot sections
        if self.bot_items:
            categories_order = ["Beginner", "Easy", "Intermediate", "Hard", "Advanced"]
            cat_map: dict[str, list[tuple[int, dict]]] = {}
            for idx, item in enumerate(self.bot_items):
                rating = int(item["profile"].get("rating", 0))
                cat = self._category_for_rating(rating)
                cat_map.setdefault(cat, []).append((idx, item))

            h_spacing = 12
            v_spacing = 14

            accent_colors = {
                "Beginner": (90, 160, 100),
                "Easy": (100, 150, 210),
                "Intermediate": (210, 180, 90),
                "Hard": (205, 110, 110),
                "Advanced": (180, 95, 205),
            }
            header_font = pygame.font.Font(None, 24)

            def draw_header(cat_name: str, y_pos: int, is_first: bool) -> int:
                if not is_first:
                    y_pos += 14
                text_surf = header_font.render(cat_name, True, (240, 240, 240))
                color = accent_colors.get(cat_name, (120, 120, 140))
                pad_x, pad_y = 10, 5
                bg_w = text_surf.get_width() + pad_x * 2
                bg_h = text_surf.get_height() + pad_y * 2
                bg_x = self.x + (self.width - bg_w) // 2
                bg_y = y_pos
                if bg_y + bg_h >= view_top and bg_y <= view_top + view_height:
                    pill = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
                    pygame.draw.rect(pill, (*color, 55), (0, 0, bg_w, bg_h), border_radius=bg_h // 2)
                    pygame.draw.rect(pill, (*color, 140), (0, 0, bg_w, bg_h), width=1, border_radius=bg_h // 2)
                    pill.blit(text_surf, (pad_x, pad_y))
                    self.screen.blit(pill, (bg_x, bg_y))
                    underline_y = bg_y + bg_h + 3
                    pygame.draw.line(self.screen, (*color, 160), (bg_x, underline_y), (bg_x + bg_w, underline_y), 2)
                    pygame.draw.line(self.screen, (*color, 70), (bg_x, underline_y + 2), (bg_x + bg_w, underline_y + 2), 1)
                    return underline_y + 6
                else:
                    return bg_y + bg_h + 6

            for cat in categories_order:
                entries = cat_map.get(cat)
                if not entries:
                    continue
                y = draw_header(cat, y, is_first=(cat == categories_order[0]))

                # Prepare entry surfaces
                name_font = pygame.font.Font(None, 18)
                rating_font = pygame.font.Font(None, 14)
                prepared = []
                for idx, item in entries:
                    profile = item["profile"]
                    name = profile.get("name", "Bot")
                    rating_val = profile.get("rating", 0)
                    name_surf = name_font.render(name, True, (210, 210, 210))
                    rating_surf = rating_font.render(str(rating_val), True, (180, 180, 180))
                    text_w = max(name_surf.get_width(), rating_surf.get_width())
                    cell_width = max(self._bot_image_size[0], text_w)
                    text_block_height = name_surf.get_height() + 2 + rating_surf.get_height()
                    cell_height = self._bot_image_size[1] + 4 + text_block_height
                    prepared.append({
                        "idx": idx,
                        "item": item,
                        "name_surf": name_surf,
                        "rating_surf": rating_surf,
                        "cell_width": cell_width,
                        "cell_height": cell_height,
                    })

                if not prepared:
                    continue
                # Uniform column width
                uniform_col_width = max(e["cell_width"] for e in prepared)
                for e in prepared:
                    e["cell_width"] = uniform_col_width

                MAX_COLS = 3
                rows: list[list[dict]] = []
                row: list[dict] = []
                for e in prepared:
                    row.append(e)
                    if len(row) == MAX_COLS:
                        rows.append(row)
                        row = []
                if row:
                    rows.append(row)

                grid_full_width = uniform_col_width * MAX_COLS + h_spacing * (MAX_COLS - 1)
                base_start_x = self.x + (self.width - grid_full_width) // 2

                row_y = y
                for row in rows:
                    start_x = base_start_x
                    max_row_h = 0
                    for e in row:
                        idx = e["idx"]
                        item = e["item"]
                        img: pygame.Surface = item["image"]
                        name_surf = e["name_surf"]
                        rating_surf = e["rating_surf"]
                        cell_width = e["cell_width"]
                        cell_height = e["cell_height"]
                        img_x = start_x + (cell_width - self._bot_image_size[0]) // 2
                        img_y = row_y
                        bg_padding = 4
                        bg_width = cell_width + bg_padding * 2
                        bg_height = cell_height + bg_padding * 2
                        bg_x = img_x - (cell_width - self._bot_image_size[0]) // 2 - bg_padding
                        bg_y = img_y - bg_padding
                        visible = bg_y + bg_height >= view_top and bg_y <= view_top + view_height
                        if visible:
                            bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
                            bg_surface.fill((70, 70, 80, 120))
                            self.screen.blit(bg_surface, (bg_x, bg_y))
                            self.screen.blit(img, (img_x, img_y))
                            name_x = bg_x + (bg_width - name_surf.get_width()) // 2
                            name_y = img_y + self._bot_image_size[1] + 4
                            rating_x = bg_x + (bg_width - rating_surf.get_width()) // 2
                            rating_y = name_y + name_surf.get_height() + 2
                            self.screen.blit(name_surf, (name_x, name_y))
                            self.screen.blit(rating_surf, (rating_x, rating_y))
                        item_rect = pygame.Rect(bg_x, bg_y, bg_width, bg_height)
                        item["rect"] = item_rect
                        if self._selected_bot_index == idx and visible:
                            pygame.draw.rect(self.screen, (200, 180, 40), item_rect, 2)
                        start_x += cell_width + h_spacing
                        max_row_h = max(max_row_h, cell_height)
                    row_y += max_row_h + v_spacing
                y = row_y + 4

        # Content height & scroll clamp
        self.content_height = (y + self.scroll_offset) - self.top
        max_scroll = max(0, self.content_height - self.height)
        if self.scroll_offset > max_scroll:
            self.scroll_offset = max_scroll

        # Scrollbar
        if self.content_height > self.height:
            track_w = 8
            track_x = self.x + self.width - track_w - 4
            track_y = self.top + 4
            track_h = self.height - 8
            pygame.draw.rect(self.screen, (55, 55, 65), (track_x, track_y, track_w, track_h), border_radius=4)
            thumb_ratio = self.height / self.content_height
            thumb_h = max(24, int(track_h * thumb_ratio))
            scroll_ratio = self.scroll_offset / (self.content_height - self.height)
            thumb_y = track_y + int((track_h - thumb_h) * scroll_ratio)
            pygame.draw.rect(self.screen, (120, 120, 140), (track_x + 1, thumb_y, track_w - 2, thumb_h), border_radius=4)

        # Restore clip
        self.screen.set_clip(prev_clip)


class TopBarButtonType(Enum):
    LEFTBUTTON = 1
    RIGHTBUTTON = 2

class TopBarButtonItem:
    def __init__(self, button : ImageButton, action, type : TopBarButtonType):
        self.button = button()
        self.action = action
        self.type = type

def settings_button_action(screen_manager: ScreenManager):
    screen_manager.set_screen("settings")
    game_state.board_settings_button_pressed = True

def back_button_action(screen_manager: ScreenManager):
    screen_manager.set_screen("menu")

def restart_button_action(board_pieces_manager: BoardPiecesManager):
    if not game_state.in_game: return

    board_pieces_manager.reset(show_p=True)

def resign_button_action(board_pieces_manager: BoardPiecesManager):
    if not game_state.in_game: return
    board_pieces_manager.resign()

class BoardPage:
    def __init__(self, screen: pygame.Surface, screen_manager: ScreenManager, board_top_bar_height: int):
        self.screen = screen
        self.board_top_bar_height = board_top_bar_height
        self.screen_manager = screen_manager
        # Side panel width
        self.side_panel_width = 260
        # Board managers
        board_width = max(320, screen.get_width() - self.side_panel_width)
        self.chess_board_manager = ChessBoardManager(screen, board_width, self.board_top_bar_height)
        self.arrow_manager = ArrowManager(self.chess_board_manager)
        self.highlight_manager = HighlightManager(self.chess_board_manager)
        self.board_pieces_manager = BoardPiecesManager(
            screen,
            self.chess_board_manager._square_size,
            self.chess_board_manager.player,
            self.board_top_bar_height,
        )
        # Side panel setup
        self.side_panel = SidePanel(self.screen, self.board_top_bar_height, self.side_panel_width)
        self.side_panel.add_text("UI Panel", size=22, color=(180, 180, 180))
        # Bot selection / rating state
        self._selected_bot_rating = None
        self._selected_bot_profile = None
        self._bot_large_image = None  # cached large surface for in-game display
        self._active_bot_profile = None  # snapshot of bot used for current game
        if not game_state.multiplayer:
            def _on_bot_select(profile: dict):
                rating = profile.get("rating", 400)
                name = profile.get("name", "Bot")
                print(f"Bot selected: {name} (rating {rating})", flush=True)
                self._selected_bot_rating = rating
                self._selected_bot_profile = profile
                # Apply rating immediately
                try:
                    self.board_pieces_manager.set_bot_rating(rating)
                except Exception:
                    pass
                # Cache large image for in-game panel
                img_path = profile.get("image_path")
                if img_path and os.path.exists(img_path):
                    try:
                        raw = pygame.image.load(img_path).convert_alpha()
                        max_w = self.side_panel_width - 40
                        max_h = int((self.screen.get_height() - self.board_top_bar_height) * 0.55)
                        iw, ih = raw.get_size()
                        scale = min(max_w / iw, max_h / ih)
                        new_size = (max(10, int(iw * scale)), max(10, int(ih * scale)))
                        self._bot_large_image = pygame.transform.smoothscale(raw, new_size)
                    except Exception:
                        self._bot_large_image = None
                else:
                    self._bot_large_image = None
                # Clear active bot profile so fresh selection is used on next game start
                self._active_bot_profile = None
            self.side_panel.add_bots(BOT_PROFILES, on_select=_on_bot_select)
        # Mouse state
        self.mouse_down = False
        self.left_mouse_down = False
        self.right_mouse_down = False
        self._right_down_square = None
        self._right_down_pos = None
        self._right_drag_threshold_px = 6
        # Top bar buttons
        self.home_button = TopBarButtonItem(BackButton, lambda: back_button_action(self.screen_manager), TopBarButtonType.LEFTBUTTON)
        self.restart_button = TopBarButtonItem(RestartButton, lambda: restart_button_action(self.board_pieces_manager), TopBarButtonType.LEFTBUTTON)
        self.resign_button = TopBarButtonItem(ResignButton, lambda: resign_button_action(self.board_pieces_manager), TopBarButtonType.LEFTBUTTON)
        self.settings_button = TopBarButtonItem(SettingsButton, lambda: settings_button_action(self.screen_manager), TopBarButtonType.RIGHTBUTTON)
        self.top_bar_static = [self.home_button, self.settings_button]
        self.last_check_pos = None
        # Bottom pane overlay configuration
        self.bottom_pane_height = 120  # increased to fit color selection boxes
        self._start_button_rect = None
        self._start_btn_padding = 16
        self._start_btn_height = 40
        self._start_btn_color_idle = (70, 140, 90)
        self._start_btn_color_hover = (90, 170, 115)
        self._start_btn_color_disabled = (80, 80, 80)
        self._start_btn_text_color = (240, 240, 240)
        self._start_btn_font = pygame.font.Font(None, 30)
        self._start_btn_hover = False
        # Color selection state
        self._color_option_rects = []
        self._selected_color_option = "white"  # default
        self._hover_color_option = None

    def display(self, event: pygame.event.Event) -> None:
        # Ensure board orientation matches assigned color in multiplayer
        if game_state.multiplayer and game_state.my_color:
            desired = game_state.my_color
            if self.chess_board_manager.player != desired:
                self.chess_board_manager.player = desired
                self.board_pieces_manager.player = desired
                # Re-render pieces with new perspective but keep layout
                self.board_pieces_manager.reset(flip=True)

        if self.last_check_pos != game_state.check_position:
            self.chess_board_manager.unset_color_red()
            self.last_check_pos = game_state.check_position
        elif self.last_check_pos is not None:
            self.last_check_pos = game_state.check_position
        if game_state.check_position is not None:
            self.chess_board_manager.set_color_red(*self.last_check_pos)
        else:
            self.chess_board_manager.unset_color_red()

        self.board_pieces_manager.add_event(event)

        # Update arrow hover early in the frame to draw the freshest preview
        if event and event.type == pygame.MOUSEMOTION and self.right_mouse_down:
            if settings_file_manager.get_setting("in_game_highlighting"):
                square_pos = self.chess_board_manager.get_square_loc(*event.pos)
                if square_pos and 1 <= square_pos[0] <= 8 and 1 <= square_pos[1] <= 8:
                    self.arrow_manager.update_hover_square(square_pos)

        # Apply debounce/timing for hover squares every frame
        self.arrow_manager.tick()

        # Fill screen and draw all components
        self.screen.fill(colors.BACKGROUND_COLOR)
        
        # Build current buttons list: use Resign in multiplayer, Restart otherwise
        action_btn = self.resign_button if game_state.multiplayer else self.restart_button
        current_buttons = [self.home_button, action_btn, self.settings_button]

        # Position left and right groups each frame to adapt to window size
        left_buttons = [btn for btn in current_buttons if btn.type == TopBarButtonType.LEFTBUTTON]
        right_buttons = [btn for btn in current_buttons if btn.type == TopBarButtonType.RIGHTBUTTON]

        last_left_button_pos = 0
        for btn in left_buttons:
            btn.button.set_position(last_left_button_pos + 10, 10)
            last_left_button_pos = btn.button.end_pos()

        last_right_button_pos = self.screen.get_width()
        for btn in right_buttons:
            btn.button.set_position(last_right_button_pos - 40, 10)
            last_right_button_pos = btn.button.start_pos()

        for btn in current_buttons:
            # Enable/disable behavior
            if btn == self.restart_button:
                if not game_state.in_game:
                    btn.button.disable()
                elif game_state.in_game and btn.button.disabled == True:
                    btn.button.enable()
            elif btn == self.resign_button:
                if not game_state.in_game:
                    btn.button.disable()
                else:
                    btn.button.enable()

            btn.button.display(self.screen)
            if not game_state.pop_up_on:
                btn.button.on_click(event, btn.action)
            else:
                btn.button.on_click(event, lambda: None)

        # --- Board & side panel drawing ---
        black_color = (0, 0, 0)
        white_color = (255, 255, 255)
        self.chess_board_manager.draw_board(black_color, white_color)

        side_panel_x = self.chess_board_manager._square_size * 8

        if game_state.in_game and not game_state.multiplayer:
            # Full-height panel (hide pre-game UI content)
            panel_height = self.screen.get_height() - self.board_top_bar_height
            pygame.draw.rect(self.screen, (30,30,38), pygame.Rect(side_panel_x, self.board_top_bar_height, self.side_panel_width, panel_height))
            # Draw selected bot large image centered
            center_rect = pygame.Rect(side_panel_x, self.board_top_bar_height, self.side_panel_width, panel_height)
            # Use active snapshot to avoid mid-game changes
            active_profile = self._active_bot_profile or self._selected_bot_profile
            img_surface = self._bot_large_image
            if active_profile is not None and img_surface is None:
                # If no cached large image (e.g., came from previous game) regenerate quickly
                img_path = active_profile.get("image_path") if isinstance(active_profile, dict) else None
                if img_path and os.path.exists(img_path):
                    try:
                        raw = pygame.image.load(img_path).convert_alpha()
                        max_w = self.side_panel_width - 40
                        max_h = int((self.screen.get_height() - self.board_top_bar_height) * 0.55)
                        iw, ih = raw.get_size()
                        scale = min(max_w/iw, max_h/ih)
                        new_size = (max(10, int(iw*scale)), max(10, int(ih*scale)))
                        img_surface = pygame.transform.smoothscale(raw, new_size)
                    except Exception:
                        img_surface = None
            if img_surface is not None:
                img = img_surface
            else:
                # Fallback placeholder
                img = pygame.Surface((120,120), pygame.SRCALPHA)
                img.fill((70,70,90))
                fnt = pygame.font.Font(None, 40)
                q = fnt.render("?", True, (220,220,220))
                img.blit(q, q.get_rect(center=(60,60)))
            iw, ih = img.get_size()
            img_x = center_rect.x + (center_rect.width - iw)//2
            img_y = center_rect.y + max(10, (center_rect.height - ih)//2 - 60)  # shift up to make room for text
            self.screen.blit(img, (img_x, img_y))
            # Name & rating
            name_font = pygame.font.Font(None, 34)
            rating_font = pygame.font.Font(None, 26)
            if active_profile:
                name_txt = active_profile.get("name", "Bot")
                rating_val = active_profile.get("rating", self._selected_bot_rating or 0)
            else:
                name_txt = "Bot"
                rating_val = self._selected_bot_rating or 0
            name_surf = name_font.render(name_txt, True, (230,230,235))
            rating_surf = rating_font.render(f"Rating {rating_val}", True, (180,180,190))
            name_x = center_rect.x + (center_rect.width - name_surf.get_width())//2
            name_y = img_y + ih + 25
            rating_x = center_rect.x + (center_rect.width - rating_surf.get_width())//2
            rating_y = name_y + name_surf.get_height() + 6
            self.screen.blit(name_surf, (name_x, name_y))
            self.screen.blit(rating_surf, (rating_x, rating_y))
        else:
            # Pre-game: show interactive side panel with scrolling content
            available_height = self.screen.get_height() - self.board_top_bar_height - self.bottom_pane_height
            if available_height < 50:
                available_height = 50
            self.side_panel.update_geometry(
                x=side_panel_x,
                top=self.board_top_bar_height,
                height=available_height
            )
            self.side_panel.draw()

        if not (game_state.in_game and not game_state.multiplayer):
            # Only show pre-game bottom pane controls when not in an active single-player game
            pane_y = self.side_panel.top + self.side_panel.height
            pane_rect = pygame.Rect(side_panel_x, pane_y, self.side_panel_width, self.bottom_pane_height)
            pygame.draw.rect(self.screen, (35, 35, 44), pane_rect)
            pygame.draw.line(self.screen, (55, 55, 65), (pane_rect.x, pane_rect.y), (pane_rect.right, pane_rect.y), 1)
            color_box_size = 26
            row_top = pane_y + 10
            gap = 8
            start_x = side_panel_x + 10
            options = ["white", "black", "random"]
            self._color_option_rects.clear()
            mouse_pos = pygame.mouse.get_pos()
            self._hover_color_option = None
            for i, opt in enumerate(options):
                rect = pygame.Rect(start_x + i * (color_box_size + gap), row_top, color_box_size, color_box_size)
                self._color_option_rects.append((opt, rect))
                if opt == "white":
                    pygame.draw.rect(self.screen, (230, 230, 230), rect, border_radius=6)
                elif opt == "black":
                    pygame.draw.rect(self.screen, (30, 30, 30), rect, border_radius=6)
                else:
                    surf = pygame.Surface((color_box_size, color_box_size))
                    surf.fill((230, 230, 230))
                    pygame.draw.polygon(surf, (30, 30, 30), [(0,0),(color_box_size-1,0),(0,color_box_size-1)])
                    self.screen.blit(surf, rect.topleft)
                if rect.collidepoint(mouse_pos):
                    self._hover_color_option = opt
                outline_color = None
                if opt == self._selected_color_option:
                    outline_color = (200, 180, 40)
                elif opt == self._hover_color_option:
                    outline_color = (140, 140, 160)
                if outline_color:
                    pygame.draw.rect(self.screen, outline_color, rect, width=3, border_radius=6)
                else:
                    pygame.draw.rect(self.screen, (60, 60, 70), rect, width=1, border_radius=6)
            # Resign & draw buttons
            icon_size = 34
            icon_gap = 10
            right_icons_top = row_top
            resign_icon_path = os.path.join('assets','icons','resign.png')
            self._resign_icon_rect = None
            self._draw_icon_rect = None
            if os.path.exists(resign_icon_path):
                resign_img = pygame.image.load(resign_icon_path).convert_alpha()
                resign_img = pygame.transform.smoothscale(resign_img, (icon_size, icon_size))
            else:
                resign_img = pygame.Surface((icon_size, icon_size))
                resign_img.fill((120,60,60))
            icon_right_x = side_panel_x + self.side_panel_width - icon_size - 10
            draw_icon_x = icon_right_x - icon_size - icon_gap
            draw_surf = pygame.Surface((icon_size, icon_size))
            draw_surf.fill((230,230,230))
            pygame.draw.rect(draw_surf, (30,30,30), (0,0,icon_size//2, icon_size))
            small_font = pygame.font.Font(None, 20)
            half_text = small_font.render("1/2", True, (200,180,40))
            draw_surf.blit(half_text, half_text.get_rect(center=(icon_size//2, icon_size//2)))
            self.screen.blit(draw_surf, (draw_icon_x, right_icons_top))
            self.screen.blit(resign_img, (icon_right_x, right_icons_top))
            self._draw_icon_rect = pygame.Rect(draw_icon_x, right_icons_top, icon_size, icon_size)
            self._resign_icon_rect = pygame.Rect(icon_right_x, right_icons_top, icon_size, icon_size)
            # Start button
            btn_width = self.side_panel_width - self._start_btn_padding * 2
            btn_x = side_panel_x + self._start_btn_padding
            btn_y = pane_y + self.bottom_pane_height - self._start_btn_height - 8
            self._start_button_rect = pygame.Rect(btn_x, btn_y, btn_width, self._start_btn_height)
            self._start_btn_hover = self._start_button_rect.collidepoint(mouse_pos)
            if game_state.in_game:
                btn_color = self._start_btn_color_disabled
                btn_text = "In Progress"
            else:
                btn_color = self._start_btn_color_hover if self._start_btn_hover else self._start_btn_color_idle
                btn_text = "Start"
            pygame.draw.rect(self.screen, btn_color, self._start_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, (255,255,255,40), self._start_button_rect, width=1, border_radius=8)
            text_surf = self._start_btn_font.render(btn_text, True, self._start_btn_text_color)
            self.screen.blit(text_surf, text_surf.get_rect(center=self._start_button_rect.center))
            # Selected bot preview (pre-game)
            if not game_state.in_game:
                preview_font = pygame.font.Font(None, 22)
                sel = self._selected_bot_profile
                if sel:
                    pv_text = f"Selected: {sel.get('name','Bot')} ({sel.get('rating','?')})"
                else:
                    pv_text = "Select a bot..."
                pv_surf = preview_font.render(pv_text, True, (200,200,210))
                pv_rect = pv_surf.get_rect()
                pv_rect.midbottom = (pane_rect.centerx, self._start_button_rect.top - 6)
                if pv_rect.left < pane_rect.left + 8:
                    pv_rect.left = pane_rect.left + 8
                if pv_rect.right > pane_rect.right - 8:
                    pv_rect.right = pane_rect.right - 8
                self.screen.blit(pv_surf, pv_rect)

        # Pieces on top of board
        self.board_pieces_manager.display()

        # Draw square highlights above pieces
        if settings_file_manager.get_setting("in_game_highlighting"):
            self.highlight_manager.draw_highlights(self.screen)
        
        # Draw arrows after the board and pieces
        if settings_file_manager.get_setting("in_game_highlighting"):
            self.arrow_manager.draw_arrows(self.screen)

        pygame.display.update()

        # Handle mouse events for interaction
        if event:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Let side panel process clicks for bot selection
                self.side_panel.handle_event(event)
                # Color option selection / Start button click
                if event.button == 1:
                    # Color option boxes
                    for opt, rect in self._color_option_rects:
                        if rect.collidepoint(event.pos):
                            self._selected_color_option = opt
                            break
                    # Resign button inside pane (only active if game in progress)
                    if self._resign_icon_rect and self._resign_icon_rect.collidepoint(event.pos):
                        if game_state.in_game:
                            resign_button_action(self.board_pieces_manager)
                    # Draw (offer draw) placeholder - could implement draw logic later
                    if self._draw_icon_rect and self._draw_icon_rect.collidepoint(event.pos):
                        # For now just print/log placeholder
                        print("draw_offer_clicked", flush=True)
                    # Start button
                    if self._start_button_rect and self._start_button_rect.collidepoint(event.pos):
                        if not game_state.in_game:
                            try:
                                # Apply selected bot rating now (fallback if none chosen)
                                # Bot rating already applied on selection; no action needed here
                                if self._selected_bot_profile is None and hasattr(self.side_panel, 'bot_items') and self.side_panel.bot_items:
                                    # Default to first bot if user didn't pick
                                    first_profile = self.side_panel.bot_items[0]["profile"]
                                    self._selected_bot_profile = first_profile
                                    self._selected_bot_rating = first_profile.get("rating", 400)
                                    try:
                                        self.board_pieces_manager.set_bot_rating(self._selected_bot_rating)
                                    except Exception:
                                        pass
                                # Snapshot active bot for this game - create a proper copy
                                if self._selected_bot_profile:
                                    try:
                                        print(f"Pre-start selected bot: {self._selected_bot_profile.get('name')} rating {self._selected_bot_profile.get('rating')}", flush=True)
                                    except Exception:
                                        pass
                                    self._active_bot_profile = {
                                        "name": self._selected_bot_profile.get("name", "Bot"),
                                        "rating": self._selected_bot_profile.get("rating", 400),
                                        "image_path": self._selected_bot_profile.get("image_path", "")
                                    }
                                    print(f"Game started with bot: {self._active_bot_profile['name']} (rating {self._active_bot_profile['rating']})", flush=True)
                                    # Re-apply rating at start to guarantee engine uses the snapshot value
                                    try:
                                        self.board_pieces_manager.set_bot_rating(self._active_bot_profile["rating"])
                                    except Exception:
                                        pass
                                else:
                                    self._active_bot_profile = {"name": "Bot", "rating": 400, "image_path": ""}
                                    print("Game started with default bot", flush=True)
                                    try:
                                        self.board_pieces_manager.set_bot_rating(400)
                                    except Exception:
                                        pass
                                chosen_color = self._selected_color_option
                                if chosen_color == "random":
                                    import random as _rnd
                                    chosen_color = _rnd.choice(["white", "black"])
                                # Set orientation
                                self.chess_board_manager.player = chosen_color
                                self.board_pieces_manager.player = chosen_color
                                # Mark game in progress before reset so engine (white) moves if user is black
                                game_state.in_game = True
                                game_state.check_position = None
                                self.board_pieces_manager.reset()
                            except Exception:
                                pass
                if event.button == 1:  # Left mouse button
                    if not self.left_mouse_down:
                        self.left_mouse_down = True
                        self.mouse_down = True
                        # Clear arrows and highlights on left-click
                        if settings_file_manager.get_setting("in_game_highlighting"):
                            self.arrow_manager.clear_arrows()
                            self.highlight_manager.clear_highlights()
                elif event.button == 3:  # Right mouse button
                    if not self.right_mouse_down:
                        self.right_mouse_down = True
                        x, y = event.pos
                        square_pos = self.chess_board_manager.get_square_loc(x, y)
                        if settings_file_manager.get_setting("in_game_highlighting"):
                            # Record down info for deciding click vs drag
                            self._right_down_square = square_pos if square_pos and 1 <= square_pos[0] <= 8 and 1 <= square_pos[1] <= 8 else None
                            self._right_down_pos = (x, y)
                            # Start arrow candidate; we'll cancel if it turns into a click
                            self.arrow_manager.start_drawing_arrow(self._right_down_square)
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    if self.left_mouse_down:
                        self.left_mouse_down = False
                        self.mouse_down = False
                        x, y = event.pos
                        square_pos = self.chess_board_manager.get_square_loc(x, y)

                        if self.board_pieces_manager.selected_piece:
                            self.board_pieces_manager.move_piece(square_pos)
                        else:
                            self.board_pieces_manager.select_piece(square_pos)
                            
                elif event.button == 3:  # Right mouse button
                    if self.right_mouse_down:
                        self.right_mouse_down = False
                        x, y = event.pos
                        square_up = self.chess_board_manager.get_square_loc(x, y)
                        # Determine if this was a drag (arrow) or click (highlight)
                        drag_px = 0
                        if self._right_down_pos is not None:
                            dx = x - self._right_down_pos[0]
                            dy = y - self._right_down_pos[1]
                            drag_px = (dx*dx + dy*dy) ** 0.5
                        if settings_file_manager.get_setting("in_game_highlighting"):
                            if self._right_down_square and drag_px <= self._right_drag_threshold_px:
                                # Treat as click: toggle highlight on the square, even if empty
                                self.highlight_manager.toggle_highlight(self._right_down_square)
                                # Cancel any in-progress arrow preview
                                self.arrow_manager.cancel_drawing()
                            else:
                                # Finish arrow if valid
                                self.arrow_manager.finish_drawing_arrow(square_up)
                        # Reset right-down tracking
                        self._right_down_square = None
                        self._right_down_pos = None
                        
            elif event.type == pygame.MOUSEMOTION:
                # Already handled above before drawing for smoother preview
                pass
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Clear all arrows on Escape key
                    if settings_file_manager.get_setting("in_game_highlighting"):
                        self.arrow_manager.clear_arrows()
                        self.highlight_manager.clear_highlights()
                elif event.key == pygame.K_c:
                    # Clear all arrows on C key (alternative)
                    if settings_file_manager.get_setting("in_game_highlighting"):
                        self.arrow_manager.clear_arrows()
                        self.highlight_manager.clear_highlights()
