import subprocess
import os
import logging
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import gspread
import sys
import time
from datetime import datetime
from google.oauth2.service_account import Credentials

print(sys.executable)

# Set up logging
logging.basicConfig(
    filename='nfl_pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# Load environment variables from .env file
load_dotenv()


def get_gsheets_client():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client


def send_email(subject, body):
    try:
        sender_email = os.getenv('EMAIL')
        receiver_email = os.getenv('RECEIVER_EMAIL')
        password = os.getenv('EMAIL_PASSWORD')

        # Set up the email server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()

        # Login to your email account
        server.login(sender_email, password)

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject

        # Attach the email body
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server.send_message(msg)
        server.quit()

        logging.info(f"Email sent: {subject}")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")


def run_script(script_name):
    try:
        print(f"Running {script_name}...")
        result = subprocess.run([os.path.join('venv', 'Scripts', 'python.exe'), script_name], check=True, capture_output=True, text=True)
        # print(f"STDOUT:\n{result.stdout}")  # Standard output
        # print(f"STDERR:\n{result.stderr}")  # Error output
        logging.info(f"ETL {script_name.split('.')[0]} pipeline completed successfully.")
        print(f"{script_name} completed successfully!\n")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e}")
        # print(f"STDOUT:\n{e.stdout}")  # Any output before error
        # print(f"STDERR:\n{e.stderr}")  # Error details
        logging.error(f"ETL {script_name.split('.')[0]} pipeline failed: {e}")


# Define log function
def log_run_to_gsheets(status, duration, error_message=''):
    try:
        # Connect to Google Sheets
        client = get_gsheets_client()
        sheet = client.open_by_key(os.getenv('SPREADSHEET_ID_LOG')).worksheet('Run_Log')

        # Record current date and time for logging
        run_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Static pipeline name for this project
        pipeline_name = "NFL Pipeline"

        # Append new row to Google Sheets
        new_row = [pipeline_name, run_date, status, duration, error_message]
        sheet.append_row(new_row)
        logging.info(f"Run log added to Google Sheets: {new_row}")

    except gspread.exceptions.APIError as api_error:
        logging.error(f"Google Sheets API error: {api_error}")
    except gspread.exceptions.SpreadsheetNotFound:
        logging.error("Google Sheets ID not found or inaccessible. Check SPREADSHEET_ID.")
    except Exception as e:
        logging.error(f"Failed to log run to Google Sheets: {e}")


def main():
    start_time = time.time()  # Track start time

    # Define the list of scripts to run
    script_folder = os.path.dirname(__file__)
    scripts = ["nfl_scrapper.py", "schedule.py", "matchup_stats.py", "write_to_gsheets.py",]

    try:
        for script in scripts:
            script_path = os.path.join(script_folder, script)
            run_script(script_path)

        duration = round(time.time() - start_time, 2)  # Calculate total duration
        log_run_to_gsheets('Success', duration)  # Log success
        subject = "NFL Pipeline Completed Successfully"
        body = "The NFL data pipeline has run successfully without any issues."
        send_email(subject, body)
        logging.info("ETL run_all_nfl_scripts pipeline completed successfully.")

    except Exception as e:
        duration = round(time.time() - start_time, 2)
        log_run_to_gsheets('Failed', duration, str(e))  # Log failure with error
        subject = "NFL Pipeline Failed"
        body = f"The NFL data pipeline encountered an error:\n\n{str(e)}"
        send_email(subject, body)
        logging.error(f"ETL run_all_nfl_scripts pipeline failed: {e}")


if __name__ == "__main__":
    main()
