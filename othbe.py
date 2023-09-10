from flask import Flask, request, jsonify, make_response
from scorer import Scorer
from notation import get_legal_moves, flip_player


# initialize flask
app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
app.config["JSON_SORT_KEYS"] = False
app.config["JSONIFY_MIMETYPE"] = "application/json;charset=utf-8"

computer_player = None

def make_computer_player():
    computer = Scorer("Walter53")
    computer.c_weight = -20
    computer.corner_weight = 10
    computer.frontier_weight = -3
    computer.move_weight = 2
    computer.piece_weight = 0
    computer.stable_weight = 5
    computer.x_weight = -30
    computer.dump_weights()
    return computer

# make an OPTIONS endpoint with path /othello
@app.route("/othello", methods=["OPTIONS"])
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

# make an OPTIONS endpoint with path /othello
@app.route("/othello/bestmove", methods=["OPTIONS"])
def _build_cors_preflight_response_2():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


# make an endpoint with path /othello
@app.route("/othello", methods=["GET"])
def othello():
    notation = request.args.get("notation", default="", type=str)
    # set up a new game
    game_state = get_legal_moves(notation)
    # return response as json
    response = jsonify(game_state)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

# make an endpoint with path /othello/bestmove
@app.route("/othello/bestmove", methods=["GET"])
def bestmove():
    notation = request.args.get("notation", default="", type=str)
    game_state = get_legal_moves(notation)
    if game_state["game_over"]:
        response = jsonify({"best_move": None})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    current_player = game_state["current_player"]
    move_scores = {}
    for m in game_state["valid_moves"]:
        new_notation = notation + m
        game_state = get_legal_moves(new_notation)
        current_player_score = computer_player.score(game_state["board"], current_player)
        opponent_score = computer_player.score(game_state["board"], flip_player(current_player))
        move_scores[m] = current_player_score - opponent_score
    best_move = max(move_scores, key=move_scores.get)
    move_scores["best_move"] = best_move
    response = jsonify(move_scores)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# start the app
if __name__ == "__main__":
    computer_player = make_computer_player()
    app.run()
