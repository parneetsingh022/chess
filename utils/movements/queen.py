def queen_moves(board, color, x, y):
    """
    Lists all possible moves for a queen piece.
    
    Args:
        board (list): The current state of the chess board.
        color (str): The color of the queen ('white' or 'black').
        x (int): The x-coordinate of the queen (1-8).
        y (int): The y-coordinate of the queen (1-8).
    
    Returns:
        list: A list of possible moves as (x, y) tuples.
    """
    x -= 1  # Convert to 0-indexed
    y -= 1  # Convert to 0-indexed

    moves = []
    directions = [
        (1, 0), (-1, 0),  # Horizontal moves
        (0, 1), (0, -1),  # Vertical moves
        (1, 1), (1, -1),  # Diagonal moves
        (-1, 1), (-1, -1)
    ]

    for dx, dy in directions:
        for step in range(1, 8):  # The queen can move up to 7 squares in any direction
            new_x = x + dx * step
            new_y = y + dy * step

            # Check if the new position is on the board
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                # Check if the square is unoccupied or occupied by an opponent's piece
                if board[new_y][new_x] == "":
                    moves.append((new_x + 1, new_y + 1))  # Convert back to 1-indexed
                elif board[new_y][new_x][0].lower() != color[0]:  # If it's occupied by an opponent's piece
                    moves.append((new_x + 1, new_y + 1))  # Convert back to 1-indexed
                    break  # Can't move further in this direction
                else:
                    break  # Can't move further if the square is occupied by the same color
            else:
                break  # Out of bounds

    return moves
