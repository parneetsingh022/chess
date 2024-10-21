def pawn_moves(board, color, x, y):
    """
    Lists all possible moves for a pawn piece.
    
    Args:
        board (list): The current state of the chess board.
        color (str): The color of the pawn ('white' or 'black').
        x (int): The x-coordinate of the pawn (1-8).
        y (int): The y-coordinate of the pawn (1-8).
    
    Returns:
        list: A list of possible moves as (x, y) tuples.
    """
    x -= 1  # Convert to 0-indexed
    y -= 1  # Convert to 0-indexed

    moves = []
    direction = -1 if color == 'white' else 1  # White moves up, black moves down
    start_row = 6 if color == 'white' else 1

    # Move forward one square (ensure within bounds)
    if 0 <= y + direction < 8 and board[y + direction][x] == "":
        moves.append((x + 1, y + 1 + direction))  # Convert back to 1-indexed
        
        # Move forward two squares if on starting row (ensure within bounds)
        if y == start_row and 0 <= y + 2 * direction < 8 and board[y + 2 * direction][x] == "":
            moves.append((x + 1, y + 1 + 2 * direction))  # Convert back to 1-indexed

    # Capture diagonally (ensure within bounds)
    if x > 0 and 0 <= y + direction < 8 and board[y + direction][x - 1] != "" and board[y + direction][x - 1][0].lower() != color[0]:
        moves.append((x, y + 1 + direction))  # Convert back to 1-indexed
    if x < 7 and 0 <= y + direction < 8 and board[y + direction][x + 1] != "" and board[y + direction][x + 1][0].lower() != color[0]:
        moves.append((x + 2, y + 1 + direction))  # Convert back to 1-indexed

    return moves
