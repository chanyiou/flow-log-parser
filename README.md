# Flow Log Parser

## Description

This Python program parses flow log data and maps each log entry to a tag based on a lookup table provided in a CSV file. The destination port and protocol combination in the flow log is used to determine which tag from the lookup table applies. The output contains counts for each tag, as well as counts for each port/protocol combination found in the flow logs.

The program handles untagged traffic, provides error logging, and outputs the results in a text file.

## Assumptions

- The flow log input file is a plain text file (ASCII) and can be up to **10 MB** in size.
- The lookup table is a CSV file containing up to **10,000 mappings**, with columns for destination port, protocol, and tag.
- Tags can be mapped to multiple port/protocol combinations.
- Matching between flow log entries and lookup table entries is **case-insensitive** (e.g., both `TCP` and `tcp` are treated equally).
- Malformed flow log entries or lookup table entries will be skipped.
- Flow log records that do not have a matching tag in the lookup table will be marked as "untagged."
- The program uses built-in Python libraries and does not require external packages.

## Input Files

1. **Flow log file**: A file containing flow log data.
Example:
```text
2 123456789010 eni-1235b8ca123456789 172.31.16.139 172.31.16.21 20641 22 6 20 4249 1418530010 1418530070 ACCEPT OK 2 123456789010 eni-1235b8ca123456789 172.31.16.139 172.31.16.21 20641 80 6 20 4249 1418530010 1418530070 ACCEPT OK
```
2. **Lookup table file**: A CSV file with the format `dstport,protocol,tag`.
Example:
```text
dstport,protocol,tag
22,tcp,sv_P1
80,tcp,sv_P2
443,tcp,sv_P3
```
## Output

The program generates two outputs:

1. **Tag Counts**: The number of matches for each tag.
2. **Port/Protocol Combination Counts**: The number of times each port and protocol combination appears in the flow log.

Example output:
```text
Tag Counts:
Tag       Count
untagged  1
sv_P1     1
sv_P2     1

Port/Protocol Combination Counts:
Port Protocol Count
22   tcp      1
80   tcp      1
```
## Logging

A log file named `flow_log_parser.log` is generated, capturing any warnings, errors, or other relevant execution information.

## Usage

### Running the Program

To run the flow log parser, use the following command:

```text
python flow_log_parser.py --flow_log flow_log.txt --lookup lookup_table.csv --output output.txt
```
Where:

- --flow_log is the input flow log file.
- --lookup is the input lookup table file.
- --output is the file where the results will be written.


Example
If you have the following input files:

flow_log.txt:
```text
2 123456789010 eni-1235b8ca123456789 172.31.16.139 172.31.16.21 20641 22 6 20 4249 1418530010 1418530070 ACCEPT OK
2 123456789010 eni-1235b8ca123456789 172.31.16.139 172.31.16.21 20641 80 6 20 4249 1418530010 1418530070 ACCEPT OK
```
lookup_table.csv:
```text
dstport,protocol,tag
22,tcp,sv_P1
80,tcp,sv_P2
```

Running the program with:
```bash
python flow_log_parser.py --flow_log flow_log.txt --lookup lookup_table.csv --output output.txt
```

output.txt will contain:
```text
Tag Counts:
Tag             Count
sv_P1           1
sv_P2           1

Port/Protocol Combination Counts:
Port   Protocol   Count
22     tcp        1
80     tcp        1
```

### Running Tests
To run unit tests for the flow log parser, use the following command:
```bash
python -m unittest test_flow_log_parser.py
```

### Generating Input Files
1. flow_log.txt:
You can use generate_flow_log.py to create a sample flow log file. The script generates a file containing flow log entries based on specified parameters.

Usage:
```bash
python generate_flow_log.py --num_entries <number_of_entries> --output_file <output_file>
```
Example:
```bash
python generate_flow_log.py --num_entries 100 --output_file flow_log.txt
```
2. lookup_table.csv:
You can use generate_lookup_table.py to create a lookup table CSV file. This script generates a CSV file containing random mappings of destination ports, protocols, and tags.

Usage:
```bash
python generate_lookup_table.py --num_mappings <number_of_mappings> --output_file <output_csv_file>
```
Example:
```bash
python generate_lookup_table.py --num_mappings 5000 --output_file lookup_table.csv
```

### Output Analysis
The output file from the flow log parser shows important details about network traffic in two main parts: Tag Counts and Port/Protocol Combination Counts. The Tag Counts section tells us how often each tag appears, which helps identify popular services; a lot of untagged entries mean we might need to update the lookup table. The Port/Protocol Combination Counts section shows how many times each port and protocol is used, helping to spot key services and potential security issues; high counts for certain ports suggest we should take a closer look.
