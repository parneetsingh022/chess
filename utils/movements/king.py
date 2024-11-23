from utils.movements.pawn import pawn_moves
from utils.movements.rook import rook_moves
from utils.movements.knight import knight_moves
from utils.movements.bishop import bishop_moves
from utils.movements.queen import queen_moves

def king_moves(board, color, x, y, king_moved, rook1_moved, rook2_moved):
    """
    Lists all possible moves for a king piece, including castling.
    
    Args:
        board (list): The current state of the chess board.
        color (str): The color of the king ('white' or 'black').
        x (int): The x-coordinate of the king (1-8).
        y (int): The y-coordinate of the king (1-8).
        king_moved (bool): Whether the king has moved.
        rook1_moved (bool): Whether the rook on the king's side has moved.
        rook2_moved (bool): Whether the rook on the queen's side has moved.
    
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

    # Castling logic
    if not king_moved:
        if color == 'white':
            # Kingside castling
            if not rook2_moved and board[7][5] == "" and board[7][6] == "":
                moves.append((7, 8))  # Convert to 1-indexed
            # Queenside castling
            if not rook1_moved and board[7][1] == "" and board[7][2] == "" and board[7][3] == "":
                moves.append((3, 8))  # Convert to 1-indexed
        else:
            # Kingside castling
            if not rook2_moved and board[0][5] == "" and board[0][6] == "":
                moves.append((7, 1))  # Convert to 1-indexed
            # Queenside castling
            if not rook1_moved and board[0][1] == "" and board[0][2] == "" and board[0][3] == "":
                moves.append((3, 1))  # Convert to 1-indexed

    return moves


def flatten(nested_list):
    return [item for sublist in nested_list for item in (flatten(sublist) if isinstance(sublist, list) else [sublist])]

def is_check(board, color):
    """
    Checks if the given color is in check.
    
    Args:
        board (list): The current state of the chess board.
        color (str): The color to check ('white' or 'black').
    
    Returns:
        bool: True if the color is in check, False otherwise.
    """
    

    king_pos = None
    color = "white" if color == "black" else "black"

    for y, row in enumerate(board):
        for x, piece in enumerate(row):
            if piece.lower() == f"{color[0]}k":
                
                king_pos = (x + 1, y + 1)

    # for row in board:
    #     for piece in row:
    #         elm = "  "
    #         if piece != "":
    #             elm = piece
    #         print(elm, end=" ")
    #     print()
    # print("\n","#"*50,"\n")

    opponent_color = 'white' if color == 'black' else 'black'
    opponents_possible_moves = []
    i = -1
    for p in flatten(board):
        i+=1
        if p and p[0].lower() == opponent_color[0]:
            piece_type = p[1].lower()

            x = i%8 + 1
            y = i//8 + 1

            if piece_type == 'p':
                opponents_possible_moves.extend(pawn_moves(board, opponent_color, x, y))
            elif piece_type == 'r':
                opponents_possible_moves.extend(rook_moves(board, opponent_color, x, y))
            elif piece_type == 'n':
                opponents_possible_moves.extend(knight_moves(board, opponent_color, x, y))
            elif piece_type == 'b':
                opponents_possible_moves.extend(bishop_moves(board, opponent_color, x, y))
            elif piece_type == 'q':
                opponents_possible_moves.extend(queen_moves(board, opponent_color, x, y))
            elif piece_type == 'k':
                opponents_possible_moves.extend(king_moves(board, opponent_color, x, y, False, False, False))
        
    return (king_pos in opponents_possible_moves), king_pos
    