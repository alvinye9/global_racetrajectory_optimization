import csv
import matplotlib.pyplot as plt
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Plot x_m and y_m values from a local Cartesian CSV file.')
parser.add_argument('input_file', type=str, help='Input CSV file with local Cartesian coordinates.')
args = parser.parse_args()

# Read the local Cartesian CSV
input_file = args.input_file
x_values = []
y_values = []

with open(input_file, 'r') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)  # Skip the header row
    for row in reader:
        x_values.append(float(row[0]))
        y_values.append(float(row[1]))

# Plot the x_m and y_m values
plt.figure(figsize=(10, 6))
plt.plot(x_values, y_values, marker='o', linestyle='-', color='b')
plt.xlabel('x_m')
plt.ylabel('y_m')
plt.title('Plot of Local Cartesian Coordinates')
plt.grid(True)
plt.axis('equal')  # Ensure equal scaling for x and y axes
plt.show()
