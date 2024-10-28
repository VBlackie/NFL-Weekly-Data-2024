import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from validation_functions import run_validations

# Set up logging
logging.basicConfig(
    filename='nfl_pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


# Function to scrape the current week's NFL schedule
def scrape_current_week_schedule(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)

    # Log the status code of the response
    logging.info(f"Request to {url} returned status code: {response.status_code}")

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        logging.error(f"Failed to retrieve {url}. Status code: {response.status_code}")
        return None

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the schedule table (by inspecting the webpage)
    table = soup.find('table', {'class': 'tr-table'})  # Adjust based on the table's class

    # Check if the table was found
    if table is None:
        logging.error("No schedule table found on the page.")
        logging.debug(f"HTML content: {soup.prettify()}")
        return None

    # Prepare lists to hold the schedule data
    schedule_data = []

    # Iterate through the rows of the table
    for row in table.find_all('tr')[1:]:  # Skip the first row (header)
        cells = row.find_all('td')
        if len(cells) == 3:  # Ensure there are exactly 3 cells: Teams, Time, and Location
            teams = cells[0].text.strip()
            time = cells[1].text.strip()
            location = cells[2].text.strip()
            schedule_data.append([teams, time, location])

    # Convert the list to a pandas DataFrame
    df = pd.DataFrame(schedule_data, columns=['Teams', 'Time', 'Location'])

    return df


# Main execution
if __name__ == "__main__":
    url = "https://www.teamrankings.com/nfl/schedules/season/"  # Modify the URL if needed
    schedule_df = scrape_current_week_schedule(url)

    try:
        if schedule_df is not None:
            # Validate the DataFrame structure and contents
            if run_validations(schedule_df, "Schedule Data", required_columns=['Teams', 'Time', 'Location']):
                logging.info("Schedule data successfully scraped and validated.")
                # Optionally, save to Excel
                schedule_df.to_excel("nfl_current_week_schedule.xlsx", index=False)
                logging.info("ETL schedule pipeline completed successfully.")
            else:
                logging.error("Validation failed for schedule_df.")
    except Exception as e:
        logging.error(f"ETL schedule pipeline failed: {e}")
