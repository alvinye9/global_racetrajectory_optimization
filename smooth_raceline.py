import csv
import os
import numpy as np
import argparse
from scipy.interpolate import splprep, splev
from scipy.spatial.distance import cdist

# Set up argument parser
parser = argparse.ArgumentParser(description='Smooth out the raceline using spline generation with lateral constraints.')
parser.add_argument('input_file', type=str, help='Input CSV file with latitude and longitude.')
parser.add_argument('smoothing_factor', type=float, default=0.5, help='Smoothing factor for the spline.')
parser.add_argument('max_lateral_movement', type=float, default=0.000005, help='Maximum lateral movement for any point.') #in degrees lat/lon (approx 0.5 m)

args = parser.parse_args()

# Construct full input and output file paths
input_file = os.path.join('./inputs/tracks', args.input_file)
output_file = os.path.join('./outputs/smoothed', os.path.splitext(args.input_file)[0] + "_smooth.csv")

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Read input CSV
latitudes = []
longitudes = []

with open(input_file, 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        latitudes.append(float(row[0]))
        longitudes.append(float(row[1]))

# Perform spline interpolation
tck, u = splprep([latitudes, longitudes], s=args.smoothing_factor)
new_points = splev(np.linspace(0, 1, len(latitudes)), tck)

# Apply lateral movement constraint
original_points = np.array(list(zip(latitudes, longitudes)))
smoothed_points = np.array(list(zip(new_points[0], new_points[1])))

for i, (orig, smooth) in enumerate(zip(original_points, smoothed_points)):
    dist = np.linalg.norm(orig - smooth)
    if dist > args.max_lateral_movement:
        direction = (smooth - orig) / dist
        smoothed_points[i] = orig + direction * args.max_lateral_movement

# Write smoothed raceline to output CSV
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    for lat, lon in smoothed_points:
        writer.writerow([lat, lon])

print(f"Smoothed raceline has been written to {output_file}")
