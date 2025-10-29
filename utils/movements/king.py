from utils.movements.pawn import pawn_moves
from utils.movements.rook import rook_moves
from utils.movements.knight import knight_moves
from utils.movements.bishop import bishop_moves
from utils.movements.queen import queen_moves

def is_square_attacked(board, x, y, attacker_color):
    """
    Checks if a square is attacked by any piece of the given color.
    
    Args:
        board (list): The current state of the chess board.
        x (int): The x-coordinate of the square to check (1-indexed).
        y (int): The y-coordinate of the square to check (1-indexed).
        attacker_color (str): The color of the pieces attacking ('white' or 'black').
    
    Returns:
        bool: True if the square is attacked, False otherwise.
    """
    x -= 1  # Convert to 0-indexed
    y -= 1  # Convert to 0-indexed
    
    for i, row in enumerate(board):
        for j, piece in enumerate(row):
            if piece and piece[0].lower() == attacker_color[0]:
                piece_type = piece[1].lower()
                
                if piece_type == 'p':
                    # Pawns attack diagonally by one square only
                    if attacker_color == 'white':
                        moves = [(j + 1 + 1, i + 1 - 1), (j + 1 - 1, i + 1 - 1)]  # Diagonal squares for white pawns
                    else:
                        moves = [(j + 1 + 1, i + 1 + 1), (j + 1 - 1, i + 1 + 1)]  # Diagonal squares for black pawns

                elif piece_type == 'r':
                    moves = rook_moves(board, attacker_color, j + 1, i + 1)
                elif piece_type == 'n':
                    moves = knight_moves(board, attacker_color, j + 1, i + 1)
                elif piece_type == 'b':
                    moves = bishop_moves(board, attacker_color, j + 1, i + 1)
                elif piece_type == 'q':
                    moves = queen_moves(board, attacker_color, j + 1, i + 1)
                elif piece_type == 'k':
                    # Special rule: King attacks only adjacent squares
                    moves = [
                        (j + dx + 1, i + dy + 1)
                        for dx, dy in [
                            (1, 0), (-1, 0), (0, 1), (0, -1),
                            (1, 1), (1, -1), (-1, 1), (-1, -1)
                        ]
                        if 0 <= j + dx < 8 and 0 <= i + dy < 8
                    ]
                else:
                    moves = []

                if (x + 1, y + 1) in moves:
                    #print(f"Square ({x + 1}, {y + 1}) is attacked by {piece} at ({j + 1}, {i + 1})")
                    return True
    return False

def king_moves(board, color, x, y, king_moved, rook1_moved, rook2_moved):
    x -= 1  # Convert to 0-indexed
    y -= 1  # Convert to 0-indexed

    moves = []
    opponent_color = 'white' if color == 'black' else 'black'

    # Regular king moves
    king_moves_offsets = [
        (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]
    for dx, dy in king_moves_offsets:
        new_x = x + dx
        new_y = y + dy

        if 0 <= new_x < 8 and 0 <= new_y < 8:
            if (board[new_y][new_x] == "" or board[new_y][new_x][0].lower() != color[0]) and \
                    not is_square_attacked(board, new_x + 1, new_y + 1, opponent_color):
                moves.append((new_x + 1, new_y + 1))  # Convert back to 1-indexed

    # Castling logic
    if not king_moved:
        if color == 'white':
            # Check if king is currently under attack (common check for both castling types)
            king_not_attacked = not is_square_attacked(board, 5, 8, 'black')
            
            # Kingside castling
            if king_not_attacked and not rook2_moved and board[7][5] == "" and board[7][6] == "" and \
                    not is_square_attacked(board, 6, 8, 'black') and \
                    not is_square_attacked(board, 7, 8, 'black'):
                moves.append((7, 8))
            # Queenside castling
            if king_not_attacked and not rook1_moved and board[7][1] == "" and board[7][2] == "" and board[7][3] == "" and \
                    not is_square_attacked(board, 4, 8, 'black') and \
                    not is_square_attacked(board, 3, 8, 'black'):
                moves.append((3, 8))
        else:
            # Check if king is currently under attack (common check for both castling types)
            king_not_attacked = not is_square_attacked(board, 5, 1, 'white')
            
            # Kingside castling
            if king_not_attacked and not rook2_moved and board[0][5] == "" and board[0][6] == "" and \
                    not is_square_attacked(board, 6, 1, 'white') and \
                    not is_square_attacked(board, 7, 1, 'white'):
                moves.append((7, 1))
            # Queenside castling
            if king_not_attacked and not rook1_moved and board[0][1] == "" and board[0][2] == "" and board[0][3] == "" and \
                    not is_square_attacked(board, 4, 1, 'white') and \
                    not is_square_attacked(board, 3, 1, 'white'):
                moves.append((3, 1))

    return moves

def is_check(board, color):
    """
    Checks if the given color is in check.
    
    Args:
        board (list): The current state of the chess board.
        color (str): The color to check ('white' or 'black').
    
    Returns:
        tuple: (bool, tuple) - True if the color is in check and the king's position.
    """
    
    king_pos = None
    color = "white" if color == "black" else "black"

    # Find king position
    for y, row in enumerate(board):
        for x, piece in enumerate(row):
            if piece.lower() == f"{color[0]}k":
                king_pos = (x + 1, y + 1)
                break
        if king_pos:
            break

    opponent_color = 'white' if color == 'black' else 'black'
    
    # Directly iterate over board without flattening
    for y, row in enumerate(board):
        for x, piece in enumerate(row):
            if piece and piece[0].lower() == opponent_color[0]:
                piece_type = piece[1].lower()
                # Convert to 1-indexed coordinates
                pos_x = x + 1
                pos_y = y + 1

                # Get moves for this piece
                moves = []
                if piece_type == 'p':
                    moves = pawn_moves(board, opponent_color, pos_x, pos_y)
                elif piece_type == 'r':
                    moves = rook_moves(board, opponent_color, pos_x, pos_y)
                elif piece_type == 'n':
                    moves = knight_moves(board, opponent_color, pos_x, pos_y)
                elif piece_type == 'b':
                    moves = bishop_moves(board, opponent_color, pos_x, pos_y)
                elif piece_type == 'q':
                    moves = queen_moves(board, opponent_color, pos_x, pos_y)
                elif piece_type == 'k':
                    moves = king_moves(board, opponent_color, pos_x, pos_y, False, False, False)
                
                # Early return if king is in the attack range of this piece
                if king_pos in moves:
                    return True, king_pos
        
    return False, king_pos
    