import random
import argparse

"""
This script generates flow logs for the default accepted and rejected traffic.
Flow log ref: https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-records-examples.html

generate_flow_log.py

This script generates a flow log file with random traffic records.

Usage:
    python generate_flow_log.py --num_records <number_of_records> --output_file <output_log_file>

Example:
    python generate_flow_log.py --num_records 100 --output_file flow_log.txt
"""

# Function to generate a random IP address
def random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

# Function to generate a flow log record
def generate_flow_log(account_id, eni_id):
    src_ip = random_ip()
    dst_ip = random_ip()
    src_port = random.randint(1024, 65535)  # Source port range
    dst_port = random.choice([22, 80, 443, 8080, 8443])  # Common destination ports like SSH, HTTP, HTTPS
    protocol = random.choice([6, 17])  # 6 is TCP, 17 is UDP
    packets = random.randint(10, 1000)
    bytes_transferred = packets * random.randint(40, 1500)
    start_time = random.randint(1600000000, 1700000000)  # Random timestamp
    end_time = start_time + random.randint(10, 100)  # Duration between 10 and 100 seconds
    action = random.choice(['ACCEPT', 'REJECT'])
    status = 'OK'

    return f"2 {account_id} {eni_id} {src_ip} {dst_ip} {src_port} {dst_port} {protocol} {packets} {bytes_transferred} {start_time} {end_time} {action} {status}"

# Function to write flow logs to a file
def write_flow_logs(file_name, num_records, account_id, eni_id):
    with open(file_name, mode='w') as file:
        for _ in range(num_records):
            log_entry = generate_flow_log(account_id, eni_id)
            file.write(log_entry + "\n")

# Main function to handle CLI arguments
def main():
    parser = argparse.ArgumentParser(
        description="Generate a flow log file with random traffic records.",
        epilog="Example usage:\npython generate_flow_log.py --num_records 100 --output_file flow_log.txt",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--num_records', type=int, required=True, help='Number of flow log records to generate')
    parser.add_argument('--output_file', type=str, required=True, help='Output log file name')

    args = parser.parse_args()

    # Parameters for the logs
    account_id = "123456789010"
    eni_id = "eni-1235b8ca123456789"
    num_records = args.num_records
    output_file = args.output_file

    # Generate and write the flow logs to file
    write_flow_logs(output_file, num_records, account_id, eni_id)

    print(f"'{output_file}' with {num_records} flow log records has been generated successfully.")

if __name__ == "__main__":
    main()
