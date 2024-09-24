import argparse
from collections import defaultdict
from typing import Dict, Tuple
import logging

"""
flow_log_parser.py

This script parses a flow log file and generates statistics based on a lookup table.

Usage:
    python flow_log_parser.py --flow_log <path_to_flow_log> --lookup <path_to_lookup_table> --output <path_to_output_file>

Example:
    python flow_log_parser.py --flow_log flow_log.txt --lookup lookup_table.csv --output output.txt
"""

# Define the types for the lookup table
LookupTable = Dict[Tuple[int, str], str]


# Configure logging
def configure_logging(log_file: str, level: str):
    """
    Configure the logging settings.

    Args:
        log_file (str): The path to the log file.
        level (str): The logging level (e.g., "INFO", "DEBUG").
    """
    logging.basicConfig(
        filename=log_file,
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="w",
    )


def load_lookup_table(file_path: str) -> LookupTable:
    """
    Load the lookup table from a CSV file.

    Args:
        file_path (str): The path to the lookup table CSV file.

    Returns:
        LookupTable: A dictionary mapping (dstport, protocol) tuples to tags.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an error reading the file.
    """
    lookup = {}
    try:
        with open(file_path, "r") as f:
            next(f)  # Skip header line
            for line_number, line in enumerate(f, start=2):
                try:
                    dstport, protocol, tag = line.strip().split(",")
                    lookup[(int(dstport), protocol.lower())] = tag.strip().lower()
                except ValueError:
                    logging.error(
                        f"Malformed line {line_number} in lookup file: {line.strip()}"
                    )
                    continue
    except FileNotFoundError:
        logging.critical(f"The lookup file '{file_path}' was not found.")
        raise
    except IOError:
        logging.critical(f"Unable to read the lookup file '{file_path}'.")
        raise
    logging.info(
        f"Successfully loaded lookup table from '{file_path}'. Total mappings: {len(lookup)}"
    )
    return lookup


def parse_flow_log(
    file_path: str, lookup: LookupTable, batch_size: int = 1000
) -> Tuple[Dict[str, int], Dict[Tuple[int, str], int]]:
    """
    Parse the flow log file and count tags and port/protocol occurrences.

    Args:
        file_path (str): The path to the flow log file.
        lookup (LookupTable): The lookup table for tag mapping.
        batch_size (int): The number of lines to process in each batch.

    Returns:
        Tuple[Dict[str, int], Dict[Tuple[int, str], int]]:
            A tuple containing two dictionaries:
            - Tag counts (tag: count)
            - Port/protocol counts ((port, protocol): count)

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an error reading the file.
    """
    tag_counts = defaultdict(int)
    port_protocol_counts = defaultdict(int)

    try:
        with open(file_path, "r") as f:
            # Skip header if present (adjust if your log file doesn't have a header)
            # next(f)
            lines_batch = []

            for line_number, line in enumerate(f, start=1):
                lines_batch.append(line.strip())

                # Process batch if we've reached the desired size
                if len(lines_batch) == batch_size:
                    process_lines(
                        lines_batch,
                        line_number,
                        lookup,
                        tag_counts,
                        port_protocol_counts,
                    )
                    lines_batch = []  # Clear the batch

            # Process any remaining lines
            if lines_batch:
                process_lines(
                    lines_batch, line_number, lookup, tag_counts, port_protocol_counts
                )

    except FileNotFoundError:
        logging.critical(f"The flow log file '{file_path}' was not found.")
        raise
    except IOError:
        logging.critical(f"Unable to read the flow log file '{file_path}'.")
        raise

    logging.info(f"Successfully parsed flow log file '{file_path}'.")
    return tag_counts, port_protocol_counts


def process_lines(
    lines: list,
    line_number_start: int,
    lookup: LookupTable,
    tag_counts: Dict[str, int],
    port_protocol_counts: Dict[Tuple[int, str], int],
):
    """
    Process a batch of lines from the flow log.

    Args:
        lines (list): A list of lines to process.
        line_number_start (int): The starting line number for logging.
        lookup (LookupTable): The lookup table for tag mapping.
        tag_counts (Dict[str, int]): The dictionary to accumulate tag counts.
        port_protocol_counts (Dict[Tuple[int, str], int]):
            The dictionary to accumulate port/protocol counts.
    """
    for i, line in enumerate(lines):
        try:
            parts = line.split()
            if len(parts) < 10:
                logging.warning(
                    f"Malformed flow log entry on line {line_number_start + i}: {line.strip()}"
                )
                continue

            dstport = int(parts[6])
            protocol = "tcp" if parts[7] == "6" else "udp"

            tag = lookup.get((dstport, protocol), "untagged")
            tag_counts[tag] += 1
            port_protocol_counts[(dstport, protocol)] += 1
        except ValueError as e:
            logging.error(
                f"Invalid data on line {line_number_start + i}: {line.strip()}. Error: {e}"
            )
            continue


def write_output(
    tag_counts: Dict[str, int],
    port_protocol_counts: Dict[Tuple[int, str], int],
    output_file: str,
) -> None:
    """
    Write the tag counts and port/protocol counts to the output file.

    Args:
        tag_counts (Dict[str, int]): The dictionary of tag counts.
        port_protocol_counts (Dict[Tuple[int, str], int]):
            The dictionary of port/protocol counts.
        output_file (str): The path to the output file.

    Raises:
        IOError: If there is an error writing to the file.
    """
    try:
        with open(output_file, "w") as f:
            # Write the tag counts header
            f.write("Tag Counts:\n")
            f.write("Tag             Count\n")
            for tag, count in tag_counts.items():
                f.write(f"{tag:<15} {count:>5}\n")

            # Write the port/protocol counts header
            f.write("\nPort/Protocol Combination Counts:\n")
            f.write("Port   Protocol   Count\n")
            for (port, protocol), count in port_protocol_counts.items():
                f.write(f"{port:<7} {protocol:<10} {count}\n")
        logging.info(f"Output successfully written to '{output_file}'.")
    except IOError:
        logging.critical(f"Unable to write to the output file '{output_file}'.")
        raise


def main():
    parser = argparse.ArgumentParser(description="Flow log parser with tag mapping.")
    parser.add_argument("--flow_log", required=True, help="Path to the flow log file")
    parser.add_argument(
        "--lookup", required=True, help="Path to the lookup table CSV file"
    )
    parser.add_argument("--output", required=True, help="Path to the output file")

    log_file = "flow_log_parser.log"
    log_level = "INFO"
    args = parser.parse_args()
    configure_logging(log_file, log_level)

    try:
        logging.info("Starting the flow log parser.")
        lookup = load_lookup_table(args.lookup)
        tag_counts, port_protocol_counts = parse_flow_log(args.flow_log, lookup)
        write_output(tag_counts, port_protocol_counts, args.output)
        logging.info("Flow log parsing completed successfully.")
    except Exception as e:
        logging.critical(f"An unexpected error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
