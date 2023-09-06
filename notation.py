import json

black = 'b'
white = 'w'
empty = '.'

def calculate_pieces_to_flip(board, row, col, player):
    # Check if the specified position is within the bounds of the board
    if row < 0 or row >= 8 or col < 0 or col >= 8:
        print("Invalid move: Position is out of bounds.")
        return None

    # Check if the specified position is already occupied
    if board[row][col] != empty:
        # print("Invalid move: Position is already occupied.")
        return None

    # Define the eight possible directions to search for opponent pieces
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Initialize a list to store the positions of opponent pieces to flip
    pieces_to_flip = []

    # Iterate through each direction to check for opponent pieces to flip
    for dr, dc in directions:
        r, c = row + dr, col + dc
        temp_pieces_to_flip = []

        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] != empty and board[r][c] != player:
            temp_pieces_to_flip.append((r, c))
            r += dr
            c += dc

        if 0 <= r < 8 and 0 <= c < 8 and board[r][c] == player:
            pieces_to_flip.extend(temp_pieces_to_flip)

    return pieces_to_flip if pieces_to_flip else None

def move_to_notation(row, col, player):
    if player == black:
        col_char = chr(col + ord('A'))
    elif player == white:
        col_char = chr(col + ord('a'))
    else:
        return None  # Invalid player

    row_number = str(row + 1)

    return col_char + row_number


def get_valid_moves_for_player(board, player):
    # Initialize a list to store valid moves
    valid_moves = []

    # Iterate through each position on the board
    for row in range(8):
        for col in range(8):
            # Check if the position is a valid move for the player
            if calculate_pieces_to_flip(board, row, col, player):
                valid_moves.append(move_to_notation(row, col, player))

    return valid_moves if valid_moves else None

def get_valid_moves(board, player):
    moves = get_valid_moves_for_player(board, player)
    if not moves:
        player = flip_player(player)
        moves = get_valid_moves_for_player(board, player)
    return moves

def make_move(board, row, col, player):
    pieces_to_flip = calculate_pieces_to_flip(board, row, col, player)

    # If there are no opponent pieces to flip in any direction, it's an invalid move
    if not pieces_to_flip:
        print("Invalid move: No opponent pieces to flip.")
        return

    # Place the player's piece on the board
    board[row][col] = player

    # Flip opponent pieces
    for r, c in pieces_to_flip:
        board[r][c] = player

def flip_player(player):
    return black if player == white else white

def notation_to_board(notation):
    # Initialize the board as an 8x8 grid with empty spaces denoted by '.'
    board = [[empty for _ in range(8)] for _ in range(8)]

    # set starting positions
    board[3][3] = white
    board[3][4] = black
    board[4][3] = black
    board[4][4] = white

    # Split the notation string into moves of length 2
    moves = [notation[i:i+2] for i in range(0, len(notation), 2)]

    # Iterate through the moves
    for move in moves:
        if move[0].isalpha() and move[0].islower():
            # It's a white move
            row = int(move[1]) - 1
            col = ord(move[0]) - ord('a')
            make_move(board, row, col, white)
        elif move[0].isalpha() and move[0].isupper():
            # It's a black move
            row = int(move[1]) - 1
            col = ord(move[0]) - ord('A')
            make_move(board, row, col, black)
        else:
            # Invalid move notation, log an error
            print("Invalid move notation: " + move)

    return board

def print_board(board):
    print("  A B C D E F G H")
    print(" +-+-+-+-+-+-+-+-+")
    for row in range(8):
        print(f"{row+1}|", end="")
        for col in range(8):
            print(board[row][col], end="|")
        print("\n +-+-+-+-+-+-+-+-+")

def identify_last_player(notation):
    if not notation:
        return white  # If the notation is empty, assume white moved last

    last_move = notation[-2]  # Get the last character of the notation

    if last_move.islower():
        return white
    elif last_move.isupper():
        return black
    else:
        return None  # Invalid notation

def get_legal_moves_json(notation):
    # Create a dictionary to store the response data
    response = {}

    # Initialize the board based on the provided notation
    board = notation_to_board(notation)

    # Identify the player who last moved
    last_player = identify_last_player(notation)

    # Determine the current player
    current_player = flip_player(last_player)

    # Get valid moves for the current player
    valid_moves = get_valid_moves_for_player(board, current_player)

    # Check if the game is over
    game_over = False
    if not valid_moves:
        # If the current player has no valid moves, check if the opponent has valid moves
        valid_moves = get_valid_moves_for_player(board, last_player)
        if not valid_moves:
            game_over = True
        else:
            current_player = last_player

    # Add data to the response dictionary
    response["current_player"] = current_player
    response["board"] = board
    response["valid_moves"] = valid_moves
    response["game_over"] = game_over

    # Convert the response dictionary to a JSON string
    return json.dumps(response)

# Example usage:
notation = "D3c5"
response_json = get_legal_moves_json(notation)
print(response_json)

