import csv

# Initialize the dictionary
OPENINGS = {}

# Read the CSV file and populate the dictionary
with open('openings.csv', mode='r', newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    for row in csv_reader:
        if len(row) == 2:
            opening, opening_name = row[0], row[1]
            OPENINGS[opening] = opening_name

# Create a Python file with the dictionary
with open('openings_data.py', mode='w') as python_file:
    python_file.write('OPENINGS = ')
    python_file.write(repr(OPENINGS))

print('Dictionary has been created and saved to openings_data.py')
