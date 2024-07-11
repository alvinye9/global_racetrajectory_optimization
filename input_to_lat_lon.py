import csv
import os
import argparse
import math
from pyproj import CRS, Transformer

# Helper Functions
def get_utm_zone(longitude):  # may not be accurate for certain areas around Norway
    return math.floor(((longitude + 180) % 360) / 6) + 1

def utm_to_latlon(utm_easting, utm_northing, latitude, longitude):
    utm_zone = get_utm_zone(longitude)
    if latitude >= 0:
        utm_proj = CRS.from_string(f'EPSG:{32600 + utm_zone}')  # Northern Hemisphere is EPSG 326xx
    else:
        utm_proj = CRS.from_string(f'EPSG:{32700 + utm_zone}')  # Southern Hemisphere is EPSG 327xx
    transformer = Transformer.from_crs(utm_proj, CRS.from_epsg(4326), always_xy=True)  # UTM to Lat/Lon
    lat, lon = transformer.transform(utm_easting, utm_northing)
    return lat, lon

# Set up argument parser
parser = argparse.ArgumentParser(description='Convert local Cartesian coordinates back to latitude and longitude.')
parser.add_argument('input_file', type=str, help='Input CSV file with local Cartesian coordinates.')
parser.add_argument('ref_lat', type=float, help='Reference latitude for the origin.')
parser.add_argument('ref_lon', type=float, help='Reference longitude for the origin.')
args = parser.parse_args()

# Construct full input and output file paths
input_file = os.path.join('./inputs/tracks', args.input_file)
output_file = os.path.join('./outputs/input_to_lat_lon', os.path.splitext(args.input_file)[0] + "_latlon.csv")

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Read input CSV
local_x = []
local_y = []

with open(input_file, 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header
    for row in reader:
        local_x.append(float(row[0]))
        local_y.append(float(row[1]))

# Convert local Cartesian to lat/lon
utm_zone = get_utm_zone(args.ref_lon)
if args.ref_lat >= 0:
    utm_proj = CRS.from_string(f'EPSG:{32600 + utm_zone}')  # Northern Hemisphere is EPSG 326xx
else:
    utm_proj = CRS.from_string(f'EPSG:{32700 + utm_zone}')  # Southern Hemisphere is EPSG 327xx
transformer_to_latlon = Transformer.from_crs(utm_proj, CRS.from_epsg(4326), always_xy=True)
transformer_to_utm = Transformer.from_crs(CRS.from_epsg(4326), utm_proj, always_xy=True)

# Get the UTM origin
x_origin, y_origin = transformer_to_utm.transform(args.ref_lon, args.ref_lat)

# Write lat/lon to output CSV
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['latitude', 'longitude'])  # Write header
    for x, y in zip(local_x, local_y):
        utm_easting = x + x_origin
        utm_northing = y + y_origin
        lon, lat = transformer_to_latlon.transform(utm_easting, utm_northing)
        writer.writerow([lat, lon])

print(f"Converted data has been written to {output_file}")
