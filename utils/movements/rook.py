def rook_moves(board, color, x, y):
    """
    Lists all possible moves for a rook piece.
    
    Args:
        board (list): The current state of the chess board.
        color (str): The color of the rook ('white' or 'black').
        x (int): The x-coordinate of the rook (1-8).
        y (int): The y-coordinate of the rook (1-8).
    
    Returns:
        list: A list of possible moves as (x, y) tuples.
    """
    x -= 1  # Convert to 0-indexed
    y -= 1  # Convert to 0-indexed

    moves = []
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Right, Left, Down, Up

    for dx, dy in directions:
        new_x, new_y = x, y

        # Move in each direction until the rook is blocked or goes off the board
        while True:
            new_x += dx
            new_y += dy

            # Check if the new position is on the board
            if not (0 <= new_x < 8 and 0 <= new_y < 8):
                break

            # Check if the square is occupied
            if board[new_y][new_x] == "":
                moves.append((new_x + 1, new_y + 1))  # Convert back to 1-indexed
            else:
                # If occupied by an opponent's piece, capture it
                if board[new_y][new_x][0].lower() != color[0]:
                    moves.append((new_x + 1, new_y + 1))  # Convert back to 1-indexed
                break  # Stop moving in this direction if a piece is blocking

    return moves
