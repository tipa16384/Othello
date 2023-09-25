import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from playerfile import choose_last_n_players
import numpy as np

# Function to parse the data into a list of lists
def parse_data():
    players = choose_last_n_players(5)
    data_list = []
    for player in players:
        name = player.name
        data_list.append([name, *player.weights])
    return data_list

data_list = parse_data()

# Extract names and values
names = [player[0] for player in data_list]
values = [player[1:] for player in data_list]

# Create positions for bars and set width for each group
n_groups = len(names)
index = np.arange(n_groups)
bar_width = 0.15

# Create a figure and axis for the grouped columnar bar chart
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the grouped columnar bar chart
for i, name in enumerate(names):
    ax.bar(index + i * bar_width, values[i], bar_width, label=name)

# Customize the plot
ax.set_ylabel("Values")
ax.set_title("Last Five Blocks")
ax.set_xticks(index + bar_width * (n_groups - 1) / 2)
ax.set_xticklabels(names)
ax.legend()

# Show the grouped columnar bar chart
plt.tight_layout()
plt.show()
