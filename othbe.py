from flask import Flask, request, jsonify, make_response
from scorer import *
from notation import get_legal_moves, flip_player
from openings import OPENINGS
import random
from playerfile import choose_last_player

# initialize flask
app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.config["JSON_SORT_KEYS"] = False
app.config["JSONIFY_MIMETYPE"] = "application/json;charset=utf-8"

computer_player = None

# Heather61
# 0.24547093234841766
# 0.6893272017767724
# 0.9416892954338969
# 0.1684839961656034
# 0.07363285005254983
# 0.008688289724121612
# 0.0350523351133627


def make_computer_player():
    computer = choose_last_player()
    print ("Computer player is", computer.name)
    return computer

# make an OPTIONS endpoint with path /othello
@app.route("/othello", methods=["OPTIONS"])
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

# make an endpoint with path /othello
@app.route("/othello", methods=["GET"])
def othello():
    do_best = request.args.get("bestmove", default=False, type=bool)
    
    if do_best:
        return bestmove()
    
    notation = request.args.get("notation", default="", type=str)
    # set up a new game
    game_state = get_legal_moves(notation)
    # return response as json
    response = jsonify(game_state)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def bestmove():
    notation = request.args.get("notation", default="", type=str)
    game_state = get_legal_moves(notation)
    if game_state["game_over"]:
        response = jsonify({"best_move": None})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    
    best_move, opening_name = find_openings(notation)
    print ("Best move", best_move, "opening name", opening_name)
    move_scores = {}
    
    if not best_move:
        current_player = game_state["current_player"]
        for m in game_state["valid_moves"]:
            new_notation = notation + m
            game_state = get_legal_moves(new_notation)
            current_player_score = computer_player.score(game_state["board"], current_player)
            print ("Move", m, "score", current_player_score)
            move_scores[m] = current_player_score
        best_move = max(move_scores, key=move_scores.get)
        print ("Best move", best_move)
        print ()
    
    move_scores["best_move"] = best_move
    move_scores["opening_name"] = opening_name
    response = jsonify(move_scores)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def find_openings(notation):
    # make a list of openings that start with notation but are longer than notation
    openings = []
    for opening in OPENINGS:
        if opening.startswith(notation) and len(opening) > len(notation):
            openings.append(opening)
    # if no opening, return None
    if len(openings) == 0:
        return (None, None)
    # choose a random opening
    opening = random.choice(openings)
    best_move = opening[len(notation):len(notation)+2]
    # name of the opening is the shortest opening that starts with notation + opening
    matching_openings = [o for o in OPENINGS if o.startswith(notation + best_move)]
    opening_name = min(matching_openings, key=len)
    
    print ("Returning opening ", OPENINGS[opening_name])
    # return the two characters that follow notation
    return (best_move, OPENINGS[opening_name])
        

# start the app
if __name__ == "__main__":
    computer_player = make_computer_player()
    app.run()
