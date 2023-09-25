import random
import scorer

FILENAME = "players.txt"

# Method to append a Scorer object to the end of the file
def append_player_to_file(player):
    with open(FILENAME, "a") as f:
        f.write(player.name + "\n")
        f.write(str(player.weights[scorer.CORNER_WEIGHT_INDEX]) + "\n")
        f.write(str(player.weights[scorer.X_WEIGHT_INDEX]) + "\n")
        f.write(str(player.weights[scorer.C_WEIGHT_INDEX]) + "\n")
        f.write(str(player.weights[scorer.STABLE_WEIGHT_INDEX]) + "\n")
        f.write(str(player.weights[scorer.PIECE_WEIGHT_INDEX]) + "\n")
        f.write(str(player.weights[scorer.FRONTIER_WEIGHT_INDEX]) + "\n")
        f.write(str(player.weights[scorer.MOVE_WEIGHT_INDEX]) + "\n")
        f.write("\n")

# Method to read all the Scorer object from the file as a list
def read_players_from_file_as_list():
    players = []
    with open(FILENAME, "r") as f:
        lines = f.readlines()
        for i in range(0, len(lines), 9):
            name = lines[i].strip()
            weights = [float(lines[i+1].strip()), float(lines[i+2].strip()), float(lines[i+3].strip()), float(lines[i+4].strip()), float(lines[i+5].strip()), float(lines[i+6].strip()), float(lines[i+7].strip())]
            players.append(scorer.Scorer(name))
            players[-1].weights = weights
    return players

# Method to read all the Scorer objects from the file as a dict with the name as key
def read_players_from_file():
    player_list = read_players_from_file_as_list()
    players = {}
    for player in player_list:
        players[player.name] = player
    return players

# Function to choose "num_players" random players from the file
def choose_random_players(num_players):
    players = read_players_from_file_as_list()
    starting_players = random.sample(players, num_players)
    starting_players[0] = players[-1]
    return starting_players

# Function to choose the last player from the file
def choose_last_player():
    return choose_last_n_players(1)[0]

# Function to choose the last "n" players from the file
def choose_last_n_players(num_players):
    players = read_players_from_file_as_list()
    return players[-num_players:]
