import random
from notation import EMPTY, get_valid_moves_for_player

# tuples indication corner positions on an 8x8 board
CORNERS = ((0, 0), (0, 7), (7, 0), (7, 7))
# tuples indicating 'X' positions on an 8x8 board
X_SQUARES = ((1, 1), (1, 6), (6, 1), (6, 6))
# tuples indicating 'C' positions on an 8x8 board
C_SQUARES = ((0, 1), (1, 0), (0, 6), (1, 7), (6, 0), (7, 1), (6, 7), (7, 6))
# dictionary mapping an X_SQUARE to its corresponding corner
X_TO_CORNER = {(1, 1): (0, 0), (1, 6): (0, 7), (6, 1): (7, 0), (6, 6): (7, 7)}
# dictionary mapping a C_SQUARE to its corresponding corner
C_TO_CORNER = {(0, 1): (0, 0), (1, 0): (0, 0), (0, 6): (0, 7), (1, 7): (0, 7),
                (6, 0): (7, 0), (7, 1): (7, 0), (6, 7): (7, 7), (7, 6): (7, 7)}

class Scorer:
    def __init__(self, name):
        self.name = name
        # all values are a random number between 0 and 1
        # weight for holding a corner
        self.corner_weight = random.random()
        # weight for the 'X' square near a blank corner (negative)
        self.x_weight = random.random()
        # weight for the 'C' square near a blank corner (negative)
        self.c_weight = random.random()
        # weight for a stable piece that isn't a corner
        self.stable_weight = random.random()
        # weight for number of pieces
        self.piece_weight = random.random()
        # weight for frontier pieces (negative)
        self.frontier_weight = random.random()
        # weight for number of available moves
        self.move_weight = random.random()

    def dump_weights(self):
        print("corner_weight: " + str(self.corner_weight))
        print("x_weight: " + str(self.x_weight))
        print("c_weight: " + str(self.c_weight))
        print("stable_weight: " + str(self.stable_weight))
        print("piece_weight: " + str(self.piece_weight))
        print("frontier_weight: " + str(self.frontier_weight))
        print("move_weight: " + str(self.move_weight))


    # a stable piece is a corner piece, a piece on an edge that is adjacent to a stable piece, or a piece not on the edge that is adjacent to two stable pieces
    def is_stable(self, response, row, col):
        board = response["board"]
        current_player = response["current_player"]
        for corner in CORNERS:
            if board[corner[0]][corner[1]] == current_player:
                return True
        # make a blank board to keep track of stable pieces
        stable_board = [[EMPTY for _ in range(8)] for _ in range(8)]
        # iterate through each piece on the board
        for row in range(8):
            for col in range(8):
                # check if the piece is stable
                if board[row][col] == current_player:
                    # check if the piece is on an edge
                    if row == 0 or row == 7 or col == 0 or col == 7:
                        stable_board[row][col] = current_player
                        continue
                    # check if the piece is adjacent to a stable piece
                    if stable_board[row-1][col] == current_player or stable_board[row+1][col] == current_player or stable_board[row][col-1] == current_player or stable_board[row][col+1] == current_player:
                        stable_board[row][col] = current_player
                        continue
            

    def score(self, board, current_player):
        score = 0
        num_corners = 0

        # add corner_weight for each corner held
        sum = 0
        for corner in CORNERS:
            if board[corner[0]][corner[1]] == current_player:
                sum += self.corner_weight
                num_corners += 1
        score += sum

        # subtract x_weight for each 'X' square near a blank corner
        sum = 0
        for x_square in X_SQUARES:
            if board[x_square[0]][x_square[1]] == current_player:
                corner = X_TO_CORNER[x_square]
                if board[corner[0]][corner[1]] == EMPTY:
                    score += self.x_weight
        
        # subtract c_weight for each 'C' square near a blank corner
        for c_square in C_SQUARES:
            if board[c_square[0]][c_square[1]] == current_player:
                corner = C_TO_CORNER[c_square]
                if board[corner[0]][corner[1]] == EMPTY:
                    score += self.c_weight

        # add piece_weight for each piece held
        for row in range(8):
            for col in range(8):
                if board[row][col] == current_player:
                    score += self.piece_weight

        # subtract frontier_weight for each non-edge piece with an empty neighbor
        for row in range(8):
            for col in range(8):
                if board[row][col] == current_player:
                    # check if the piece is on an edge
                    if row == 0 or row == 7 or col == 0 or col == 7:
                        continue
                    # check if the piece has an empty neighbor
                    if board[row-1][col] == EMPTY or board[row+1][col] == EMPTY or board[row][col-1] == EMPTY or board[row][col+1] == EMPTY:
                        score -= self.frontier_weight
                    # also the diagonal neighbors
                    elif board[row-1][col-1] == EMPTY or board[row-1][col+1] == EMPTY or board[row+1][col-1] == EMPTY or board[row+1][col+1] == EMPTY:
                        score += self.frontier_weight

        # add move_weight for each available move
        valid_moves = get_valid_moves_for_player(board, current_player)
        if valid_moves:
            score += len(valid_moves) * self.move_weight

        return score

            
    def __str__(self):
        return self.name