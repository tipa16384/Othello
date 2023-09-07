from notation import get_legal_moves, print_board
from curses import wrapper
import random
import time

def display_board(stdscr, board, hit_db_count, notation):
    # clear screen
    stdscr.clear()
    stdscr.addstr(10, 0, "Hit DB: " + str(hit_db_count))
    stdscr.addstr(0, 1, "  A B C D E F G H")
    for i in range(8):
        stdscr.addstr(i+1, 1, str(i+1))
    for i in range(0, len(notation), 2):
        row = (i//2) % 9
        col = 25 + ((i//2) // 9) * 3
        stdscr.addstr(row, col, notation[i:i+2])
    for row in range(8):
        for col in range(8):
            # set cursor position
            stdscr.move(row+1, col*2+3)
            stdscr.addstr(board[row][col])
    # update screen
    stdscr.refresh()
        

# loop forever until a key is pressed
def main(stdscr):
    stdscr.nodelay(True)
    notation = ""
    hit_db_count = 0
    while True:
        c = stdscr.getch()
        if c != -1:
            break
        response = get_legal_moves(notation)
        if response['hit_db']:
            hit_db_count += 1
        display_board(stdscr, response["board"], hit_db_count, notation)
        if response["game_over"]:
            notation = ""
            # sleep one half second
            time.sleep(0.5)
        # choose a random move
        else:
            notation += random.choice(response["valid_moves"])['m']

wrapper(main)



if __name__ == "__main__":
    notation = "D3c5D6e3F4c6F5c3C4b5E2e6D2f6B3g5B4g3"
    response = get_legal_moves(notation)
    print_board(response["board"])
    print("Current player: " + response["current_player"])
    print("Annotation: " + response["annotation"])
    print("Valid moves: " + str(response["valid_moves"]))
    if response["game_over"]:
        print ("The game is over.")
        if response["black_score"] > response["white_score"]:
            print("Black wins!")
        elif response["white_score"] > response["black_score"]:
            print("White wins!")
        else:
            print("It's a tie!")
    if response["player_passed"]:
        print("The current player had no valid moves and has automatically passed.")
    print("Black and white scores: " + str(response["black_score"]) + ", " + str(response["white_score"]))
