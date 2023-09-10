from notation import get_legal_moves, flip_player, BLACK, WHITE
from curses import wrapper
import random
import time
from scorer import Scorer

# list of 50 common first names for both boys and girls
FIRST_NAMES = [
    "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia", "Harper", "Evelyn",
    "Liam", "Noah", "William", "James", "Oliver", "Benjamin", "Elijah", "Lucas", "Mason", "Logan",
    "Jacob", "Michael", "Ethan", "Daniel", "Henry", "Jackson", "Sebastian", "Aiden", "Matthew", "Samuel",
    "David", "Joseph", "Carter", "Owen", "Wyatt", "John", "Jack", "Luke", "Jayden", "Dylan",
    "Grayson", "Levi", "Isaac", "Gabriel", "Julian", "Mateo", "Anthony", "Jaxon", "Lincoln", "Joshua"
]


# function to return a random name with a random integer appended
def get_random_name():
    return random.choice(FIRST_NAMES) + str(random.randint(1, 100))

def display_board(stdscr, board, players, win_record):
    # clear screen
    stdscr.clear()
    banner = '{} ({}) vs. {} ({})'.format(players[BLACK].name, win_record[BLACK], players[WHITE].name, win_record[WHITE])
    stdscr.addstr(0, 40, banner)
    stdscr.addstr(0, 1, "  A B C D E F G H")
    for i in range(8):
        stdscr.addstr(i+1, 1, str(i+1))
    for row in range(8):
        for col in range(8):
            # set cursor position
            stdscr.move(row+1, col*2+3)
            stdscr.addstr(board[row][col])
    if win_record[BLACK] >= win_record[WHITE]:
        players[BLACK].dump_weights(stdscr, 40)
    else:
        players[WHITE].dump_weights(stdscr, 40)
    # update screen
    stdscr.refresh()

def play_one_game(players, win_record):
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
            move_scores[move] = players[player].score(response["board"], response["current_player"])
        # choose the move with the highest score
        best_move = max(move_scores, key=move_scores.get)
        notation += best_move

    if response["black_score"] > response["white_score"]:
        win_record[BLACK] += 1
    elif response["white_score"] > response["black_score"]:
        win_record[WHITE] += 1
    else:
        win_record[BLACK] += 0.5
        win_record[WHITE] += 0.5

    return response        

def battle(stdscr, players, win_record):
    for _ in range(1):
        response = play_one_game(players, win_record)
    display_board(stdscr, response["board"], players, win_record)
    if win_record[BLACK] >= win_record[WHITE]:
        players[WHITE] = Scorer(get_random_name())
    else:
        players[BLACK] = Scorer(get_random_name())
    

# loop forever until a key is pressed
def main(stdscr):
    players = { BLACK: Scorer(get_random_name()), WHITE: Scorer(get_random_name()) }

    stdscr.nodelay(True)
    while True:
        c = stdscr.getch()
        if c != -1:
            break
        win_record = { BLACK: 0, WHITE: 0 }
        battle(stdscr, players, win_record)


if __name__ == "__main__":
    wrapper(main)
