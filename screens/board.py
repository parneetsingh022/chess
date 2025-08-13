from constants import colors, fonts
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
        self.chess_board_manager = ChessBoardManager(screen, screen.get_width(), self.board_top_bar_height)
        self.board_pieces_manager = BoardPiecesManager(
            screen, self.chess_board_manager._square_size, self.chess_board_manager.player, self.board_top_bar_height
        )
        self.arrow_manager = ArrowManager(self.chess_board_manager)
        self.highlight_manager = HighlightManager(self.chess_board_manager)

        # Mouse state
        self.mouse_down = False
        self.left_mouse_down = False
        self.right_mouse_down = False
        # Track right-click origin to decide between click-highlight and drag-arrow
        self._right_down_square = None
        self._right_down_pos = None
        self._right_drag_threshold_px = 6

        # Top bar buttons
        self.home_button = TopBarButtonItem(BackButton, lambda: back_button_action(self.screen_manager), TopBarButtonType.LEFTBUTTON)
        self.restart_button = TopBarButtonItem(RestartButton, lambda: restart_button_action(self.board_pieces_manager), TopBarButtonType.LEFTBUTTON)
        self.resign_button = TopBarButtonItem(ResignButton, lambda: resign_button_action(self.board_pieces_manager), TopBarButtonType.LEFTBUTTON)
        self.settings_button = TopBarButtonItem(SettingsButton, lambda: settings_button_action(self.screen_manager), TopBarButtonType.RIGHTBUTTON)

        # Base buttons always present; action buttons will be chosen per frame
        self.top_bar_static = [
            self.home_button,
            self.settings_button,
        ]

        self.last_check_pos = None

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
        black_color = (0, 0, 0)
        white_color = (255, 255, 255)

        self.chess_board_manager.draw_board(black_color, white_color)
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
