def king_moves(board, color, x, y, king_moved):
    """
    Lists all possible moves for a king piece.
    
    Args:
        board (list): The current state of the chess board.
        color (str): The color of the king ('white' or 'black').
        x (int): The x-coordinate of the king (1-8).
        y (int): The y-coordinate of the king (1-8).
    
    Returns:
        list: A list of possible moves as (x, y) tuples.
    """
    x -= 1  # Convert to 0-indexed
    y -= 1  # Convert to 0-indexed

    moves = []
    king_moves_offsets = [
        (1, 0), (-1, 0), (0, 1), (0, -1),  # Horizontal and vertical moves
        (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonal moves
    ]

    for dx, dy in king_moves_offsets:
        new_x = x + dx
        new_y = y + dy

        # Check if the new position is on the board
        if 0 <= new_x < 8 and 0 <= new_y < 8:
            # Check if the square is unoccupied or occupied by an opponent's piece
            if board[new_y][new_x] == "" or board[new_y][new_x][0].lower() != color[0]:
                moves.append((new_x + 1, new_y + 1))  # Convert back to 1-indexed

    return moves
