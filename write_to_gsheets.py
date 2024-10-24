import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(
    filename='nfl_pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

#Loading dotenv private variables
load_dotenv()


# Set up Google Sheets API client
def get_gsheets_client():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client


# Upload Excel file to Google Sheets
def upload_to_gsheets(excel_file, spreadsheet_id, sheet_name):
    # Load the Excel sheet into pandas
    df = pd.read_excel(excel_file)

    # Replace any NaN, inf, or -inf values with an empty string or a specific value like 0
    df = df.replace([float('inf'), float('-inf'), pd.NA, None], 0)
    df = df.fillna(0)  # Replace any remaining NaN values with 0

    # Authenticate and open the spreadsheet
    client = get_gsheets_client()
    sheet = client.open_by_key(spreadsheet_id)

    # Select the desired sheet by name
    worksheet = sheet.worksheet(sheet_name)

    # Clear the existing content in the sheet
    worksheet.clear()

    # Convert the DataFrame to a list of lists and update the Google Sheets
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())


if __name__ == "__main__":
    # Path to the Excel file you want to upload
    excel_file = 'nfl_output.xlsx'

    # Google Sheets details
    spreadsheet_id = os.getenv('SPREADSHEET_ID')  # Replace with your Google Sheet ID
    sheet_name = 'Sheet1'  # Replace with the name of the sheet you want to update

    try:
        upload_to_gsheets(excel_file, spreadsheet_id, sheet_name)
        logging.info("ETL pipeline completed successfully.")
    except Exception as e:
        logging.error(f"ETL pipeline failed: {e}")
