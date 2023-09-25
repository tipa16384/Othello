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

CORNER_WEIGHT_INDEX = 0
X_WEIGHT_INDEX = 1
C_WEIGHT_INDEX = 2
STABLE_WEIGHT_INDEX = 3
PIECE_WEIGHT_INDEX = 4
FRONTIER_WEIGHT_INDEX = 5
MOVE_WEIGHT_INDEX = 6
NUM_WEIGHTS = 7

FILE_NAME = "players.txt"

# list of 50 common first names for both boys and girls
FIRST_NAMES = [
    "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia", "Harper", "Evelyn",
    "Liam", "Noah", "William", "James", "Oliver", "Benjamin", "Elijah", "Lucas", "Mason", "Logan",
    "Jacob", "Michael", "Ethan", "Daniel", "Henry", "Jackson", "Sebastian", "Aiden", "Matthew", "Samuel",
    "David", "Joseph", "Carter", "Owen", "Wyatt", "John", "Jack", "Luke", "Jayden", "Dylan",
    "Grayson", "Levi", "Isaac", "Gabriel", "Julian", "Mateo", "Anthony", "Jaxon", "Lincoln", "Joshua",
    "Andrew", "Allyson", "Shannon", "Lynn", "Brenda", "Tom", "Beatrice", "David", "Clara",
    "Eleanor", "Joan", "Clyde", "Lester", "Elizabeth", "Paul", "Richard", "Jane", "Deborah", "Edna",
    "Hillary", "Atticus", "Brian", "Jennifer", "Jazzmin", "Vallerie", "Ellie", "Ilsa", "Arnie",
    "Heather", "Adam", "Judy", "Corwin", "Katherine", "Lochinvar", "Nostromo", "Lannister", "Whitten"
]

# function to return a random name with a random integer appended
def get_random_name():
    return random.choice(FIRST_NAMES) + str(random.randint(1, 100))

# return the rows and columns in sequence, optionally filtered by a function
def row_col_generator(f = lambda r, c: True):
    for row in range(8):
        for col in range(8):
            if f(row, col):
                yield (row, col)

class Scorer:
    def __init__(self, name=None):

        self.name = name if name else get_random_name()
        
        # weights is an array of NUM_WEIGHTS random numbers
        self.weights = [random.random() for _ in range(NUM_WEIGHTS)]

    def dump_weights(self):
        print("name: " + self.name)
        print("corner_weight: " + str(self.weights[CORNER_WEIGHT_INDEX]))
        print("x_weight: " + str(self.weights[X_WEIGHT_INDEX]))
        print("c_weight: " + str(self.weights[C_WEIGHT_INDEX]))
        print("stable_weight: " + str(self.weights[STABLE_WEIGHT_INDEX]))
        print("piece_weight: " + str(self.weights[PIECE_WEIGHT_INDEX]))
        print("frontier_weight: " + str(self.weights[FRONTIER_WEIGHT_INDEX]))
        print("move_weight: " + str(self.weights[MOVE_WEIGHT_INDEX]))
        print()
    
    def dump_weights_to_file(self):
        # open file for appending
        with open(FILE_NAME, "a") as f:
            # write name and weights to file
            f.write(self.name + "\n")
            f.write(str(self.weights[CORNER_WEIGHT_INDEX]) + "\n")
            f.write(str(self.weights[X_WEIGHT_INDEX]) + "\n")
            f.write(str(self.weights[C_WEIGHT_INDEX]) + "\n")
            f.write(str(self.weights[STABLE_WEIGHT_INDEX]) + "\n")
            f.write(str(self.weights[PIECE_WEIGHT_INDEX]) + "\n")
            f.write(str(self.weights[FRONTIER_WEIGHT_INDEX]) + "\n")
            f.write(str(self.weights[MOVE_WEIGHT_INDEX]) + "\n")
            f.write("\n")
    
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

    def find_stability(self, board):
        # make map with key being position of piece and value being a map with DIRECTIONS as keys and value False
        #print ("find_stability current player {}".format(current_player))
        instability_map = {}
        for row, col in row_col_generator(lambda r, c: board[r][c] != EMPTY):
            instability_map[(row, col)] = {}
            for direction in DIRECTIONS:
                instability_map[(row, col)][direction] = False

        # iterate through each piece on the board
        for piece_pos in instability_map:
            stable_piece_color = board[piece_pos[0]][piece_pos[1]]
            # iterate through each direction
            for direction in instability_map[piece_pos]:
                # are there only player pieces or the edge of the board in this direction?
                if self.is_stable_direction(board, stable_piece_color, piece_pos, direction) or \
                    self.is_stable_direction(board, stable_piece_color, piece_pos, (-direction[0], -direction[1])):
                    instability_map[piece_pos][direction] = True
                elif self.safe_direction(board, stable_piece_color, piece_pos, direction) and \
                    self.safe_direction(board, stable_piece_color, piece_pos, (-direction[0], -direction[1])):
                    instability_map[piece_pos][direction] = True
        
        # stablity_map is a dict with key being position and value being True if all four of the directions in the corresponding instability_map is True
        stability_map = {}
        for piece_pos in instability_map:
            stability_map[piece_pos] = all(instability_map[piece_pos][direction] \
                                           for direction in instability_map[piece_pos])

        #print ("Returning stability_map")

        return stability_map                    

    def score(self, board, current_player):
        stability_map = self.find_stability(board)

        score = 0

        # add corner_weight for each corner held
        xsum = sum(self.weights[CORNER_WEIGHT_INDEX] \
                   for corner in CORNERS \
                    if board[corner[0]][corner[1]] == current_player)
        score += xsum

        # subtract x_weight for each unstable 'X' square near a blank corner
        xsum = sum(self.weights[X_WEIGHT_INDEX] \
                   for x_square in X_SQUARES \
                    if board[x_square[0]][x_square[1]] == current_player \
                        and not stability_map[x_square] \
                            and board[X_TO_CORNER[x_square][0]][X_TO_CORNER[x_square][1]] == EMPTY)
        score -= xsum

        # subtract c_weight for each unstable 'C' square near a blank corner
        xsum = sum(self.weights[C_WEIGHT_INDEX] \
                   for c_square in C_SQUARES \
                    if board[c_square[0]][c_square[1]] == current_player \
                        and not stability_map[c_square] \
                            and board[C_TO_CORNER[c_square][0]][C_TO_CORNER[c_square][1]] == EMPTY)
        score -= xsum

        # add move_weight for each available move
        valid_moves = get_valid_moves_for_player(board, current_player)
        if valid_moves:
            score += len(valid_moves) * self.weights[MOVE_WEIGHT_INDEX]
        
        # subtract double move_weight for each available move for the opponent
        valid_moves = get_valid_moves_for_player(board, flip_player(current_player))
        if valid_moves:
            score -= 2 * len(valid_moves) * self.weights[MOVE_WEIGHT_INDEX]

        # subtract FRONTIER_WEIGHT for each unstable piece of my own
        xsum = sum(self.weights[FRONTIER_WEIGHT_INDEX] \
                   for row, col in row_col_generator(lambda r, c: board[r][c] == current_player \
                                                     and not stability_map[(r, c)]))
        score -= xsum

        # add PIECE_WEIGHT for each of our pieces
        xsum = sum(self.weights[PIECE_WEIGHT_INDEX] \
                     for row, col in row_col_generator(lambda r, c: board[r][c] == current_player))
        score += xsum

        return score
    
    def __str__(self):
        return self.name