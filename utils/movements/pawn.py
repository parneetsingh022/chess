def pawn_moves(board, color, x, y, en_passant_target=None):
    """
    Lists all possible moves for a pawn piece, including en passant.

    Args:
        board (list[list[str]]): The current state of the chess board (8x8) with piece codes like 'WP', 'BP', etc., or '' for empty.
        color (str): The color of the pawn ('white' or 'black').
        x (int): The x-coordinate of the pawn (1-8).
        y (int): The y-coordinate of the pawn (1-8).
        en_passant_target (tuple[int,int] | None): If set, the board square (1-8,1-8) that can be captured en passant this move.

    Returns:
        list[tuple[int,int]]: A list of possible moves as (x, y) tuples (1-indexed).
    """
    x -= 1  # Convert to 0-indexed
    y -= 1  # Convert to 0-indexed

    moves = []
    direction = -1 if color == 'white' else 1  # White moves up (towards smaller y), black moves down
    start_row = 6 if color == 'white' else 1

    # Forward one square
    ny = y + direction
    if 0 <= ny < 8 and board[ny][x] == "":
        moves.append((x + 1, ny + 1))

        # Forward two squares from starting rank
        ny2 = y + 2 * direction
        if y == start_row and 0 <= ny2 < 8 and board[ny2][x] == "":
            moves.append((x + 1, ny2 + 1))

    # Diagonal captures
    for dx in (-1, 1):
        nx = x + dx
        ny = y + direction
        if 0 <= nx < 8 and 0 <= ny < 8:
            if board[ny][nx] != "" and board[ny][nx][0].lower() != color[0]:
                moves.append((nx + 1, ny + 1))

    # En passant capture
    if en_passant_target is not None:
        target_x, target_y = en_passant_target
        target_x -= 1
        target_y -= 1
        # Target must be exactly one forward-diagonal square and the adjacent square must contain an enemy pawn
        if target_y == y + direction and abs(target_x - x) == 1:
            adj_x = target_x
            adj_y = y  # The pawn being captured sits adjacent on the same rank as the moving pawn
            if 0 <= adj_x < 8 and 0 <= adj_y < 8:
                adj_piece = board[adj_y][adj_x]
                if adj_piece and adj_piece[1] == 'P' and adj_piece[0].lower() != color[0] and board[target_y][target_x] == "":
                    moves.append((target_x + 1, target_y + 1))

    return moves
