import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


# Function to scrape table from URL and generate DataFrame
def scrape_to_df(url):
    # Add headers to simulate a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Send a GET request to the webpage with headers
    response = requests.get(url, headers=headers)

    # Print the status code of the response
    print(f"Request to {url} returned status code: {response.status_code}")

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}. Status code: {response.status_code}")
        return None, None

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Try to find the table in the page
    table = soup.find('table')

    # Check if the table was found
    if table is None:
        print("No table found on the page. Here's the HTML content for inspection:")
        print(soup.prettify())  # Print the HTML to help with debugging
        return None, None

    # Extract the table headers (column names)
    headers = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())

    # Extract the rows of the table
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip the first row (headers)
        cells = []
        for td in tr.find_all('td'):
            cells.append(td.text.strip())
        rows.append(cells)

    # Create a pandas DataFrame
    df = pd.DataFrame(rows, columns=headers)

    # Extract the identifier from the URL (e.g., 'points-per-game')
    identifier = url.split('/')[-1]

    # Create a variable name dynamically for the DataFrame
    df_name = f"df_{identifier.replace('-', '_')}"[:31]

    # Add a short delay to avoid overwhelming the server
    time.sleep(5)  # Delay for 2 seconds

    # Return the DataFrame and the dynamic name
    return df, df_name


# Example usage:
# url = "https://www.teamrankings.com/nfl/stat/points-per-game"
# df, df_name = scrape_to_df(url)
#
# if df is not None:
#     print(f"DataFrame Name: {df_name}")
#     print(df.head())


def save_dfs_to_excel(dfs, file_name="nfl_stats.xlsx"):
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        # Loop through the list of DataFrames and their names
        for df, df_name in dfs:
            # Write each DataFrame to a separate sheet
            df.to_excel(writer, sheet_name=df_name, index=False)
    print(f"DataFrames saved to {file_name}")


# List of links to be scrapped
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


# List to store all DataFrames and their names
all_dfs = []

# Loop through the URLs, scrape the data, and store in the list
for url in urls:
    df, df_name = scrape_to_df(url)
    if df is not None:
        print(f"DataFrame Name: {df_name}")
        print(df.head())
        all_dfs.append((df, df_name))

# Save all DataFrames to an Excel file
save_dfs_to_excel(all_dfs)
