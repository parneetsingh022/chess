def knight_moves(board, color, x, y):
    """
    Lists all possible moves for a knight piece.
    
    Args:
        board (list): The current state of the chess board.
        color (str): The color of the knight ('white' or 'black').
        x (int): The x-coordinate of the knight (1-8).
        y (int): The y-coordinate of the knight (1-8).
    
    Returns:
        list: A list of possible moves as (x, y) tuples.
    """
    x -= 1  # Convert to 0-indexed
    y -= 1  # Convert to 0-indexed

    moves = []
    knight_moves_offsets = [
        (2, 1), (2, -1), (-2, 1), (-2, -1),
        (1, 2), (1, -2), (-1, 2), (-1, -2)
    ]  # All possible moves for a knight

    for dx, dy in knight_moves_offsets:
        new_x = x + dx
        new_y = y + dy

        # Check if the new position is on the board
        if 0 <= new_x < 8 and 0 <= new_y < 8:
            # Check if the square is unoccupied or occupied by an opponent's piece
            if board[new_y][new_x] == "" or board[new_y][new_x][0].lower() != color[0]:
                moves.append((new_x + 1, new_y + 1))  # Convert back to 1-indexed

    return moves
