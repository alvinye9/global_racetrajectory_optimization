import csv
import os
import argparse
import math
from pyproj import CRS, Transformer

# Helper Functions
def get_utm_zone(longitude):  # may not be accurate for certain areas around Norway
    return math.floor(((longitude + 180) % 360) / 6) + 1

def latlon_to_utm(latitude, longitude):
    utm_zone = get_utm_zone(longitude)
    if latitude >= 0:
        utm_proj = CRS.from_string(f'EPSG:{32600 + utm_zone}')  # Northern Hemisphere is EPSG 326xx
    else:
        utm_proj = CRS.from_string(f'EPSG:{32700 + utm_zone}')  # Southern Hemisphere is EPSG 327xx
    transformer = Transformer.from_crs(CRS.from_epsg(4326), utm_proj, always_xy=True)  # Lat/Lon CRS on the WGS84 reference ellipsoid is EPSG 4326
    utm_easting, utm_northing = transformer.transform(longitude, latitude)
    return utm_easting, utm_northing

# Set up argument parser
parser = argparse.ArgumentParser(description='Convert lat/long to local Cartesian and add constant columns.')
parser.add_argument('input_file', type=str, help='Input CSV file with latitude and longitude.')
parser.add_argument('w_tr_right_m', type=float,default=5.0, help='Constant value for the right track width.') # meters
parser.add_argument('w_tr_left_m', type=float, default=5.0, help='Constant value for the left track width.') # meters
args = parser.parse_args()

# Read input CSV
input_file = os.path.join('./inputs/tracks', args.input_file)
output_file = os.path.join('./outputs/input_to_local_cartesian', os.path.splitext(args.input_file)[0] + "_utm.csv")
output_file_local_cartesian = os.path.join('./outputs/input_to_local_cartesian', os.path.splitext(args.input_file)[0] + "_local_cartesian.csv")
# output_file = os.path.splitext(input_file)[0] + "_utm.csv"
# output_file_local_cartesian = os.path.splitext(input_file)[0] + "_local_cartesian.csv"

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(input_file, 'r') as csvfile:
    reader = csv.reader(csvfile)
    rows = list(reader)

# Convert lat/long to local Cartesian and write to new CSV
utm_coordinates = []
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['# x_m', 'y_m', 'w_tr_right_m', 'w_tr_left_m'])  # Write header
    for row in rows:
        lat = float(row[0])
        long = float(row[1])
        x, y = latlon_to_utm(lat, long)
        writer.writerow([x, y, args.w_tr_right_m, args.w_tr_left_m])
        utm_coordinates.append((x, y))

print(f"Converted data has been written to {output_file}")

# Write to local Cartesian CSV
x_origin, y_origin = utm_coordinates[0]
with open(output_file_local_cartesian, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['# x_m', 'y_m', 'w_tr_right_m', 'w_tr_left_m'])  # Write header
    for x, y in utm_coordinates:
        x_local = x - x_origin
        y_local = y - y_origin
        writer.writerow([x_local, y_local, args.w_tr_right_m, args.w_tr_left_m])

print(f"Converted data has been written to {output_file_local_cartesian}")
