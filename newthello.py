from notation import get_legal_moves, BLACK, WHITE, flip_player
from curses import wrapper
from scorer import *
from collections import defaultdict
from itertools import combinations
import random
from playerfile import *

winner = None

NUM_PLAYERS = 20

def display_board(stdscr, board, players, player_scores):
    # clear screen
    stdscr.clear()
    banner = '{} ({}) vs. {} ({})'.format(players[BLACK].name, player_scores[players[BLACK]], players[WHITE].name, player_scores[players[WHITE]])
    stdscr.addstr(0, 40, banner)
    stdscr.addstr(0, 1, "  A B C D E F G H")
    for i in range(8):
        stdscr.addstr(i+1, 1, str(i+1))
    for row in range(8):
        for col in range(8):
            # set cursor position
            stdscr.move(row+1, col*2+3)
            stdscr.addstr(board[row][col])
    # if win_record[BLACK] >= win_record[WHITE]:
    #     players[BLACK].dump_weights(stdscr, 40)
    # else:
    #     players[WHITE].dump_weights(stdscr, 40)
    # update screen
    stdscr.refresh()

def play_one_game(players, player_scores):
    notation = ""
    while True:
        response = get_legal_moves(notation)
        player = response["current_player"]
        if response["game_over"]:
            break
        move_scores = {}
        for move in response["valid_moves"]:
            response = get_legal_moves(notation + move)
            response["current_player"] = player
            score = players[player].score(response["board"], response["current_player"])
            move_scores[move] = score
        # choose the move with the highest score
        best_move = max(move_scores, key=move_scores.get)
        notation += best_move

    if response["black_score"] > response["white_score"]:
        player_scores[players[BLACK]] += 1
    elif response["white_score"] > response["black_score"]:
        player_scores[players[WHITE]] += 1
    else:
        player_scores[players[BLACK]] += 0.5
        player_scores[players[WHITE]] += 0.5

    return response        

def battle(stdscr, players, player_scores):
    response = play_one_game(players, player_scores)
    display_board(stdscr, response["board"], players, player_scores)
    
def get_next_generation(player_rank):
    # given a list of tuples (player, score) sorted by score, apply a genetic algorithm to create a new generation
    # the top NUM_PLAYERS/2 players are copied to the next generation
    # mutation rate is 10%
    # crossover rate is 90%
    # the bottom NUM_PLAYERS/2 players are replaced by crossover and mutation
    potential_parents = [player for player, _ in player_rank[:NUM_PLAYERS//2]]
    next_generation = []
    for _ in range(NUM_PLAYERS):
        while True:
            p1 = random.choice(potential_parents)
            p2 = random.choice(potential_parents)
            if p1 != p2:
                break
        new_player = Scorer()
        for i in range(NUM_WEIGHTS):
            if random.random() > 0.1:
                if random.random() < 0.9:
                    new_player.weights[i] = p1.weights[i]
                else:
                    new_player.weights[i] = p2.weights[i]
        next_generation.append(new_player)
    
    next_generation[-1] = Scorer()
    
    return next_generation


# loop forever until a key is pressed
def main(stdscr):
    global winner

    end_the_battle = False

    # players is a list of NUM_PLAYERS Scorer objects
    all_players = choose_random_players(NUM_PLAYERS)

    # player_scores is a dictionary of player names and scores, using defaultdict to initialize score to 0
    player_scores = defaultdict(int)

    stdscr.nodelay(True)
    while not end_the_battle:
        for p1, p2 in combinations(all_players, 2):
            c = stdscr.getch()
            if c != -1:
                end_the_battle = True
                break
            battle(stdscr, { BLACK: p1, WHITE: p2}, player_scores)
            battle(stdscr, { BLACK: p2, WHITE: p1}, player_scores)

        # set player_rank to be a list of tuples (player, score) sorted by score
        player_rank = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)

        # return the player with the highest score
        winner = player_rank[0][0]

        append_player_to_file(winner)

        all_players = get_next_generation(player_rank)
        player_scores = defaultdict(int)

if __name__ == "__main__":
    wrapper(main)
    print("The winner is {}".format(winner))
    winner.dump_weights()

