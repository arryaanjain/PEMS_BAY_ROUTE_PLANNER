"""
Extract sensor IDs from adj_mx_bay.pkl and create sensor_locations.csv template

This script extracts the 325 PeMS station IDs from your adjacency matrix.
"""

import pickle
from pathlib import Path

# Load adjacency matrix
adj_mx_path = Path('ml_models/adj_mx_bay.pkl')

with open(adj_mx_path, 'rb') as f:
    data = pickle.load(f, encoding='latin1')  # Handle Python 2 pickles

# Extract sensor IDs (they're in the first list)
sensor_ids = data[0]

print(f"✅ Found {len(sensor_ids)} sensors")
print(f"Sample sensor IDs: {sensor_ids[:10]}")

# Save station IDs to text file
output_txt = Path('ml_models/station_ids.txt')
with open(output_txt, 'w') as f:
    for station_id in sensor_ids:
        f.write(f"{station_id}\n")

print(f"\n📋 Saved all station IDs to: {output_txt}")

# Create CSV template
output_csv = Path('ml_models/sensor_locations_template.csv')
with open(output_csv, 'w') as f:
    # Write header
    f.write("sensor_id,lat,lng\n")
    
    # Write each sensor (sensor_id is the index 0-324)
    for idx in range(len(sensor_ids)):
        f.write(f"{idx},0.0,0.0\n")

print(f"\n✅ Created template CSV: {output_csv}")
print(f"\nYour PeMS Station IDs:")
for i in range(0, min(20, len(sensor_ids)), 5):
    print(f"  {', '.join(sensor_ids[i:i+5])}")
print(f"  ... ({len(sensor_ids)} total)")

print(f"\n" + "="*60)
print(f"WHERE TO GET LAT/LNG COORDINATES:")
print(f"="*60)
print(f"\n1. 🎯 EASIEST: Search GitHub for these datasets:")
print(f"   - 'PEMS-BAY sensor locations'")
print(f"   - 'PEMS Bay graph_sensor_locations'")
print(f"   - Look in repos like: DCRNN, STGCN, Graph WaveNet")
print(f"\n2. 🌐 PeMS Website (requires account):")
print(f"   - Visit: https://pems.dot.ca.gov")
print(f"   - District 4 (Bay Area) -> VDS Locations")
print(f"\n3. ✅ OR: Just keep using the approximate grid!")
print(f"   - Your system is ALREADY WORKING with approximations")
print(f"   - Good enough for testing and demos")
print(f"\n" + "="*60)
