import json
import csv
import time
from argparse import ArgumentParser

from log_filter import LogFilter

if __name__ == '__main__':
    parser = ArgumentParser(description="Apply Kalman filter to a JSON log file")
    parser.add_argument("filename", help="input json file", metavar="FILE")
    args = parser.parse_args()

    start_time = time.time()

    # Open the game log
    print("Reading {} ...".format(args.filename))
    data = open(args.filename, 'r').read()
    data_json = json.loads(data[1:-1])  # Ugly fix to read json files

    # Apply the Kalman filter on the data
    log_filter = LogFilter(data_json)
    csv_content = log_filter.apply_filter()

    # Output a csv file
    csv_filename = "{}.csv".format(args.filename)
    print("Outputting to {} ...".format(csv_filename))

    with open(csv_filename, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_content)

    print("Operation completed in {} seconds".format(time.time() - start_time))
