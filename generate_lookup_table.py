import csv
import random
import argparse

"""
generate_lookup_table.py

This script generates a CSV file containing random mappings of dstport, protocol, and tag.

Usage:
    python generate_lookup_table.py --num_mappings <number_of_mappings> --output_file <output_csv_file>

Example:
    python generate_lookup_table.py --num_mappings 5000 --output_file lookup_table.csv
"""

# List of common ports
COMMON_PORTS = [
    21, 22, 23, 25, 53, 67, 68, 80, 110, 123,
    143, 161, 162, 194, 443, 465, 587, 669, 993, 995,
    8080, 8443, 3306, 5432, 6379, 27017, 28017, 50000
]

# Function to generate random mappings
def generate_mappings(num):
    protocols = ['tcp', 'udp']
    tags = [f'sv_P{i + 1}' for i in range(num // 2)]  # Generate unique tags
    mappings = [['dstport', 'protocol', 'tag']]  # CSV header
    for _ in range(num):
        dstport = random.choice(COMMON_PORTS)  # Choose a common port
        protocol = random.choice(protocols)
        tag = random.choice(tags)
        mappings.append([dstport, protocol, tag])
    return mappings

# Function to write mappings to CSV
def write_csv(file_name, mappings):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(mappings)

# Main function to handle CLI arguments
def main():
    parser = argparse.ArgumentParser(description="Generate a lookup table with random port mappings.")
    parser.add_argument('--num_mappings', type=int, required=True, help='Number of mappings to generate')
    parser.add_argument('--output_file', type=str, required=True, help='Output CSV file name')

    args = parser.parse_args()

    num_mappings = args.num_mappings
    output_file = args.output_file

    # Generate the mappings
    mappings = generate_mappings(num_mappings)

    # Write to the specified CSV file
    write_csv(output_file, mappings)

    print(f"'{output_file}' with {num_mappings} mappings has been generated successfully.")

if __name__ == "__main__":
    main()
