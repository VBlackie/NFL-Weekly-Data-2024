import gspread
from google.oauth2.service_account import Credentials
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file


# Load credentials and Google Sheets client
def get_gsheets_client():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
    client = gspread.authorize(credentials)
    return client


# Fetch data from Google Sheets
def fetch_pipeline_data():
    client = get_gsheets_client()
    sheet = client.open_by_key(os.getenv('SPREADSHEET_ID_LOG')).worksheet('Run_Log')
    data = sheet.get_all_records()
    return data


# Prepare data for Jinja2 template
def prepare_data(data):
    pipelines = {}
    logs = []

    for row in data:
        # Aggregate latest status by pipeline
        pipeline_name = row['Pipeline Name']
        if pipeline_name not in pipelines or pipelines[pipeline_name]['run_date'] < row['Run Date']:
            pipelines[pipeline_name] = {
                'name': pipeline_name,
                'status': row['Run Status'],
                'run_date': row['Run Date'],
                'duration': row['Duration']
            }
        logs.append({
            'run_date': row['Run Date'],
            'pipeline_name': pipeline_name,
            'status': row['Run Status'],
            'duration': row['Duration'],
            'error_message': row['Error Message']
        })

    return list(pipelines.values()), logs


# Render HTML
def render_html(pipelines, logs):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('dashboard_template.html')
    output_from_parsed_template = template.render(pipelines=pipelines, logs=logs)

    with open("dashboard.html", "w") as f:
        f.write(output_from_parsed_template)


if __name__ == "__main__":
    data = fetch_pipeline_data()
    pipelines, logs = prepare_data(data)
    render_html(pipelines, logs)
