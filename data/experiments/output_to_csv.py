import re
import csv
import os
from pathlib import Path

def parse_schedules(input_file):
    input_file = Path(input_file)
    output_csv = input_file.with_suffix(".csv")
    schedules = []

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into schedule blocks
    schedule_blocks = re.split(r'\n(?=Schedule \d+ \|)', content)

    for block in schedule_blocks:
        if not block.strip():
            continue

        # Extract schedule number and final EU from the header
        header_match = re.search(r'Schedule (\d+) \| Final EU:\s*([-+]?\d*\.?\d+)', block)
        if not header_match:
            continue

        schedule_number = int(header_match.group(1))
        final_eu = float(header_match.group(2))

        # Count operation lines by counting "EU:" occurrences inside the block
        schedule_length = len(re.findall(r'EU:\s*[-+]?\d*\.?\d+', block))

        schedules.append([schedule_number, final_eu, schedule_length])

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["schedule_number", "expected_utility", "schedule_length"])
        writer.writerows(schedules)

    print(f"Wrote {output_csv}")


def batch_parse_schedules(folder_path):
    folder = Path(folder_path)

    if not folder.is_dir():
        raise ValueError(f"Not a valid folder: {folder_path}")

    txt_files = sorted(folder.glob("*.txt"))

    if not txt_files:
        print("No .txt files found.")
        return

    for txt_file in txt_files:
        parse_schedules(txt_file)


if __name__ == "__main__":
    # Change this to your folder path
    print(os.getcwd())
    batch_parse_schedules("data/experiments/world_1")
    batch_parse_schedules("data/experiments/world_2")