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

# Load environment variables
load_dotenv()


# Set up Google Sheets API client
def get_gsheets_client():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    try:
        credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        client = gspread.authorize(credentials)
        logging.info("Successfully authenticated Google Sheets API client.")
        return client
    except Exception as e:
        logging.error(f"Failed to authenticate Google Sheets API client: {e}")
        raise


# Upload Excel file to Google Sheets
def upload_to_gsheets(excel_file, spreadsheet_id, sheet_name):
    try:
        df = pd.read_excel(excel_file)
        df = df.replace([float('inf'), float('-inf'), pd.NA, None], 0).fillna(0)
        logging.info(f"Loaded data from {excel_file} with {len(df)} rows.")

        client = get_gsheets_client()
        sheet = client.open_by_key(spreadsheet_id)
        worksheet = sheet.worksheet(sheet_name)

        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        logging.info(f"Data successfully written to Google Sheets sheet '{sheet_name}'.")

    except Exception as e:
        logging.error(f"Failed to upload data to Google Sheets: {e}")
        raise


if __name__ == "__main__":
    excel_file = 'nfl_output.xlsx'
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    sheet_name = 'Sheet1'

    try:
        upload_to_gsheets(excel_file, spreadsheet_id, sheet_name)
        logging.info("write_to_gsheets.py completed successfully.")
    except Exception as e:
        logging.error(f"write_to_gsheets.py failed: {e}")
