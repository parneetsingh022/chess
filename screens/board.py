from constants import colors, fonts
import pygame

from utils.screen_manager import ScreenManager
from utils.chess_board_manager import ChessBoardManager
from utils.board_pieces_manager import BoardPiecesManager
from utils.pieces import PieceType, PieceColor, Piece

class BoardPage:
    def __init__(self, screen: pygame.Surface, screen_manager: ScreenManager):
        self.screen = screen
        self.screen_manager = screen_manager
        self.chess_board_manager = ChessBoardManager(screen, screen.get_width())
        # self.board_pieces_manager = BoardPiecesManager(
        #     screen, 
        #     self.chess_board_manager._square_size,
        #     self.chess_board_manager.player
        # )

        self.piece1 = Piece(
            screen,
            self.chess_board_manager._square_size,
            self.chess_board_manager.player,
            PieceType.KING, 
            PieceColor.BLACK
        )

    def display(self, event: pygame.event.Event) -> None:
        self.screen.fill(colors.BACKGROUND_COLOR)

        # Define the color for the black box
        black_color = (0, 0, 0)
        white_color = (255, 255, 255)

        self.chess_board_manager.draw_board(black_color, white_color)
        self.piece1.display(1,1)
        