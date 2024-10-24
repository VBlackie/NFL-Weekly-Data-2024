import subprocess
import os
import logging

# Set up logging
logging.basicConfig(
    filename='nfl_pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


def run_script(script_name):
    # Use subprocess to run the Python script
    try:
        print(f"Running {script_name}...")
        subprocess.run(["python", script_name], check=True)
        print(f"{script_name} completed successfully!\n")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")


def main():
    # Define the list of scripts to run
    script_folder = os.path.dirname(__file__)  # Get current directory of the script
    scripts = ["nfl_scrapper.py", "schedule.py", "matchup_stats.py","write_to_gsheets.py"]

    # Loop over each script and run it
    try:
        for script in scripts:
            script_path = os.path.join(script_folder, script)
            run_script(script_path)
        logging.info("ETL run_all_nfl_scripts pipeline completed successfully.")
    except Exception as e:
        logging.error(f"ETL run_all_nfl_scripts pipeline failed: {e}")


if __name__ == "__main__":
    main()
