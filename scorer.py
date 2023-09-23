import random
from notation import EMPTY, get_valid_moves_for_player, flip_player

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

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1)]

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
    
    def is_stable_direction(self, board, current_player, piece_pos, direction):
        # return True if there are only player pieces or the edge of the board in this direction
        #print ("is_stable_direction current player {} piece_pos {} direction {}".format(current_player, piece_pos, direction))
        row = piece_pos[0]
        col = piece_pos[1]
        dr = direction[0]
        dc = direction[1]
        r = row + dr
        c = col + dc
        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == current_player:
            r += dr
            c += dc
        #print ("is_stable_direction return")
        return r < 0 or r >= 8 or c < 0 or c >= 8

    def safe_direction(self, board, current_player, piece_pos, direction):
        # return True if there are zero or more player pieces followed by an opponent piece in this direction
        #print ("safe_direction current player {} piece_pos {} direction {}".format(current_player, piece_pos, direction))
        opponent_player = flip_player(current_player)
        row = piece_pos[0]
        col = piece_pos[1]
        dr = direction[0]
        dc = direction[1]
        r = row + dr
        c = col + dc
        while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == current_player:
            r += dr
            c += dc
        #print ("safe_direction return")
        return 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent_player

    def find_stability(self, board, current_player):
        # make map with key being position of piece and value being a map with DIRECTIONS as keys and value False
        #print ("find_stability current player {}".format(current_player))
        stability_map = {}
        for row in range(8):
            for col in range(8):
                if board[row][col] == current_player:
                    stability_map[(row, col)] = {}
                    for direction in DIRECTIONS:
                        stability_map[(row, col)][direction] = False

        # iterate through each piece on the board
        for piece_pos in stability_map:
            # iterate through each direction
            for direction in stability_map[piece_pos]:
                # are there only player pieces or the edge of the board in this direction?
                if self.is_stable_direction(board, current_player, piece_pos, direction) or \
                    self.is_stable_direction(board, current_player, piece_pos, (-direction[0], -direction[1])):
                    stability_map[piece_pos][direction] = True
                elif self.safe_direction(board, current_player, piece_pos, direction) and \
                    self.safe_direction(board, current_player, piece_pos, (-direction[0], -direction[1])):
                    stability_map[piece_pos][direction] = True

        #print ("Returning stability_map")

        return stability_map                    

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
                    score -= self.x_weight
        
        # subtract c_weight for each 'C' square near a blank corner
        for c_square in C_SQUARES:
            if board[c_square[0]][c_square[1]] == current_player:
                corner = C_TO_CORNER[c_square]
                if board[corner[0]][corner[1]] == EMPTY:
                    score -= self.c_weight

        # add piece_weight for each piece held
        for row in range(8):
            for col in range(8):
                if board[row][col] == current_player:
                    score += self.piece_weight

        # add move_weight for each available move
        valid_moves = get_valid_moves_for_player(board, current_player)
        if valid_moves:
            score += len(valid_moves) * self.move_weight

        stability_map = self.find_stability(board, current_player)
        #print ("stability_map {}".format(stability_map))
        #self.print_stability_map(stability_map)
        # for each stable piece, count Trues in the direction map
        for piece_pos in stability_map:
            #print ("piece_pos {} stability_map[piece_pos] {}".format(piece_pos, stability_map[piece_pos]))
            count = self.count_stable_directions(stability_map, piece_pos)
            if count == 4:
                score += self.stable_weight
            else:
                score -= (4 - count) * self.frontier_weight

        return score
    
    def count_stable_directions(self, stability_map, piece_pos):
        count = 0
        for direction in stability_map[piece_pos]:
            if stability_map[piece_pos][direction]:
                count += 1
        return count

    def print_stability_map(self, stability_map):
        print("   A B C D E F G H")
        for row in range(8):
            print(row + 1, end="  ")
            for col in range(8):
                pos = (row, col)
                if pos not in stability_map:
                    c = EMPTY
                else:
                    count = self.count_stable_directions(stability_map, pos)
                    c = str(count)
                print(c, end=" ")
            print()

    def __str__(self):
        return self.name