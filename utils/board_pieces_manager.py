import pygame

class BoardPiecesManager:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.image = pygame.image.load("assets/chess_pieces.png").convert_alpha()
        self.piece_width = 128  # Assuming each piece is 128x128 pixels
        self.piece_height = 128

    def extract_piece(self, row, col):
        """
        Extract a piece based on its row and column in the grid.

        Args:
            row (int): The row of the piece in the grid.
            col (int): The column of the piece in the grid.

        Returns:
            pygame.Surface: The surface containing the extracted piece.
        """
        rect = pygame.Rect(col * self.piece_width, row * self.piece_height, self.piece_width, self.piece_height)
        return self.image.subsurface(rect)

    def display_piece(self, x, y, row, col):
        """
        Display the extracted piece on the screen at the specified coordinates and draw a rectangle around it.

        Args:
            x (int): The x-coordinate to display the piece.
            y (int): The y-coordinate to display the piece.
            row (int): The row of the piece in the grid.
            col (int): The column of the piece in the grid.

        Returns:
            None
        """
        piece = self.extract_piece(row, col)

        # Calculate the new size for the piece
        new_size = (self.screen.get_width() // 8, self.screen.get_height() // 8)

        # Resize the piece
        resized_piece = pygame.transform.scale(piece, new_size)

        # Display the resized piece on the screen
        self.screen.blit(resized_piece, (x, y))