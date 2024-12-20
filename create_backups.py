import os
import shutil
import logging
from datetime import datetime
import time
import pandas as pd

# Set up logging
logging.basicConfig(
    filename='nfl_pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Load environment variables if needed
# load_dotenv()

# Define backup paths
BACKUP_DIR = "backups"
RAW_DATA_DIR = os.path.join(BACKUP_DIR, "raw_data")
PROCESSED_DATA_DIR = os.path.join(BACKUP_DIR, "processed_data")
FINAL_OUTPUT_DIR = os.path.join(BACKUP_DIR, "final_output")
LOG_DIR = os.path.join(BACKUP_DIR, "logs")
MAIN_OUTPUT_FILE = 'nfl_output.xlsx'
BACKUP_FOLDER = 'backups/final_output/'

# Create backup directories if they don’t exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FINAL_OUTPUT_DIR, LOG_DIR]:
    os.makedirs(dir_path, exist_ok=True)


# Function to backup nfl_output.xlsx with a timestamp
def backup_nfl_output_with_timestamp():
    # Ensure the backup directory exists
    os.makedirs(BACKUP_FOLDER, exist_ok=True)

    # Load the existing nfl_output.xlsx file
    if os.path.exists(MAIN_OUTPUT_FILE):
        final_df = pd.read_excel(MAIN_OUTPUT_FILE)
        current_date = datetime.now().strftime('%Y-%m-%d')
        backup_filename = f"nfl_output_{current_date}.xlsx"
        backup_path = os.path.join(BACKUP_FOLDER, backup_filename)

        # Save the DataFrame with a timestamped filename
        final_df.to_excel(backup_path, index=False)
        logging.info(f"Backup created: '{backup_path}'")
        # print(f"Backup created: '{backup_path}'")
        return backup_path  # Return path for logging if needed
    else:
        logging.warning(f"File '{MAIN_OUTPUT_FILE}' does not exist. No backup created.")
        # print(f"File '{MAIN_OUTPUT_FILE}' does not exist. No backup created.")
        return None


def backup_file(source_path, backup_folder):
    try:
        if os.path.exists(source_path):
            backup_path = os.path.join(backup_folder, os.path.basename(source_path))
            shutil.copy2(source_path, backup_path)
            logging.info(f"Backed up {source_path} to {backup_path}")
        else:
            logging.warning(f"File not found, skipping backup: {source_path}")
    except Exception as e:
        logging.error(f"Failed to back up {source_path}: {e}")


def clean_old_backups(directory, days=30):
    now = time.time()
    cutoff = now - (days * 86400)  # 86400 seconds per day

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff:
            os.remove(file_path)
            logging.info(f"Removed old backup: {file_path}")


def main():
    # Define files to back up
    raw_files = ['nfl_stats.xlsx', 'nfl_current_week_schedule.xlsx']  # Add other raw files here
    # processed_files = ['intermediate_file.xlsx']  # Example, add processed files if any
    final_files = ["nfl_output.xlsx"]
    log_files = ['nfl_pipeline.log']

    # Back up nfl_output to datestamp
    backup_path = backup_nfl_output_with_timestamp()
    if backup_path:
        print(f"Backup successful: {backup_path}")
    else:
        print("Backup failed or file not found.")

    # Back up each type of file
    for file in raw_files:
        backup_file(file, RAW_DATA_DIR)
    # for file in processed_files:
    #     backup_file(file, PROCESSED_DATA_DIR)
    for file in final_files:
        backup_file(file, FINAL_OUTPUT_DIR)
    for file in log_files:
        backup_file(file, LOG_DIR)


if __name__ == "__main__":
    main()
