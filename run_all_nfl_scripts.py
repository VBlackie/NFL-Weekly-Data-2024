import subprocess
import os


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
    scripts = ["main.py", "schedule.py", "matchup stats.py","write_to_gsheets.py"]

    # Loop over each script and run it
    for script in scripts:
        script_path = os.path.join(script_folder, script)
        run_script(script_path)


if __name__ == "__main__":
    main()
