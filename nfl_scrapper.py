import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from validation_functions import run_validations

# Set up logging
logging.basicConfig(
    filename='nfl_pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


# Function to scrape table from URL and generate DataFrame
def scrape_to_df(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)
    print(f"Request to {url} returned status code: {response.status_code}")

    if response.status_code != 200:
        logging.error(f"Failed to retrieve {url}. Status code: {response.status_code}")
        return None, None

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')

    if table is None:
        logging.error(f"No table found on the page: {url}")
        return None, None

    headers = [th.text.strip() for th in table.find_all('th')]
    rows = [[td.text.strip() for td in tr.find_all('td')] for tr in table.find_all('tr')[1:]]

    df = pd.DataFrame(rows, columns=headers)
    identifier = url.split('/')[-1]
    df_name = f"df_{identifier.replace('-', '_')}"[:31]

    time.sleep(5)

    if not run_validations(df, df_name, required_columns=headers):
        logging.error(f"Validation failed for {df_name}")
        return None, None

    return df, df_name


def save_dfs_to_excel(dfs, file_name="nfl_stats.xlsx"):
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        for df, df_name in dfs:
            df.to_excel(writer, sheet_name=df_name, index=False)
    print(f"DataFrames saved to {file_name}")


def main():
    urls = [
        "https://www.teamrankings.com/nfl/stat/points-per-game",
        "https://www.teamrankings.com/nfl/stat/opponent-points-per-game",
        "https://www.teamrankings.com/nfl/stat/sacks-per-game",
        "https://www.teamrankings.com/nfl/stat/third-down-conversion-pct",
        "https://www.teamrankings.com/nfl/stat/qb-sacked-per-game",
        "https://www.teamrankings.com/nfl/stat/opponent-third-down-conversion-pct",
        "https://www.teamrankings.com/nfl/stat/turnover-margin-per-game",
        "https://www.teamrankings.com/nfl/stat/penalty-yards-per-game",
        "https://www.teamrankings.com/nfl/stat/red-zone-scoring-pct",
        "https://www.teamrankings.com/nfl/stat/opponent-red-zone-scores-per-game"
    ]

    all_dfs = []
    for url in urls:
        df, df_name = scrape_to_df(url)
        if df is not None:
            print(f"DataFrame Name: {df_name}")
            print(df.head())
            all_dfs.append((df, df_name))

    try:
        save_dfs_to_excel(all_dfs)
        logging.info("ETL nfl_scrapper pipeline completed successfully.")
    except Exception as e:
        logging.error(f"ETL nfl_scrapper pipeline failed: {e}")


if __name__ == "__main__":
    main()
