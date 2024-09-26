import pandas as pd


# Function to load the Excel file into a dictionary of pandas DataFrames
def load_data(file_path):
    # Load all sheets into a dictionary of DataFrames
    data = pd.read_excel(file_path, sheet_name=None)
    for sheet_name, df in data.items():
        print(f"Sheet: {sheet_name}")
        print(df.columns)  # This will print column names for each sheet
    return data


# Function to extract teams from the Week 4 sheet
def extract_teams(schedule_df):
    # Assuming the team matchups are in the column 'Thu Sep 26'
    teams = []
    for row in schedule_df['Thu Sep 26'].dropna():
        if ' @ ' in row:  # Check if the row contains the separator '@'
            team_1, team_2 = row.split(' @ ')
            teams.append((team_1.strip(), team_2.strip()))  # Add both teams, stripped of any spaces
    return teams


# Function to extract data for a given team from specified sheets
# Function to extract data for a given team from specified sheets
# Function to extract data for a given team from specified sheets
# Function to extract data for a given team from specified sheets, and calculate Rank sum and average
def build_team_data(team_name, data, sheets_to_process):
    # Create an empty list to store the result
    team_data = []
    rank_sum = 0
    rank_count = 0

    # Iterate over the sheets specified in sheets_to_process
    for sheet_name in sheets_to_process:
        df = data[sheet_name]

        # Ensure team names are stripped of spaces
        df['Team'] = df['Team'].str.strip()

        # Filter the row where the team name matches
        team_row = df[df['Team'] == team_name]

        # If a row was found, process its data
        if not team_row.empty:
            # Convert 'Rank' column to int if it exists and accumulate the sum
            if 'Rank' in team_row.columns:
                team_row['Rank'] = team_row['Rank'].astype(int)
                rank_sum += team_row['Rank'].values[0]
                rank_count += 1

            # Drop 'Team' column and convert the row to a flattened list
            team_row = team_row.drop(columns=['Team']).values.flatten().tolist()

            # Append the data from this sheet to the main team data list
            team_data.extend(team_row)

    # Calculate the average rank
    rank_average = rank_sum / rank_count if rank_count > 0 else 0

    # Append the Rank sum and Rank average to the team data
    team_data.append(rank_sum)
    team_data.append(rank_average)

    # Return the combined data for the team as a single row (list)
    return team_data


def main():
    file_path = "path_to_your_file.xlsx"
    data = load_data('NFL Weekly Data.xlsx')

    # Define the sheets you want to process (excluding 'Week 4' and 'Sheet1')
    sheets_to_process = ['Third Down Conversion', 'QB Sacked per Game', 'Opponent Third Down Conversion',
                         'Turnover Margin', 'Yards Penalized', 'Redzone Scoring', 'Opponent Redzone Scoring']

    # Extract teams from Week 4 sheet
    week_4_schedule = data['Week 4']
    teams = extract_teams(week_4_schedule)

    # Create an empty list to store data for all teams
    all_teams_data = []

    # Iterate over all teams in the schedule
    for team_1, team_2 in teams:
        print(f"Processing {team_1} and {team_2}")

        # Build data for each team and append to the list
        team_1_data = build_team_data(team_1, data, sheets_to_process)
        team_2_data = build_team_data(team_2, data, sheets_to_process)

        # Add team names at the beginning of each row for clarity
        team_1_data.insert(0, team_1)
        team_2_data.insert(0, team_2)

        # Append both teams' data to the all_teams_data list
        all_teams_data.append(team_1_data)
        all_teams_data.append(team_2_data)

        # Add a blank row between matchups
        all_teams_data.append([''] * len(team_1_data))

    # Define the correct pattern of columns for one set of stats
    column_pattern = ['Rank', '2024', 'Last 3', 'Last 1', 'Home', 'Away', '2023']

    # Create the column names dynamically by repeating the pattern for each sheet's stats
    columns = ['Team'] + [f"{col}_{sheet_name}" for sheet_name in sheets_to_process for col in column_pattern]

    # Add Rank Sum and Rank Average to the column names
    columns.extend(['Rank Sum', 'Rank Average'])

    # Convert the list to a DataFrame
    all_teams_df = pd.DataFrame(all_teams_data, columns=columns)

    # Display the final DataFrame
    print(all_teams_df)

    # Print the DataFrame to verify
    print(all_teams_df.head())  # Check the first few rows to confirm the Rank Sum and Rank Average
    print(all_teams_df.columns)  # Check the column names

    # Optionally, save the DataFrame to an Excel file
    with pd.ExcelWriter("all_teams_data.xlsx", engine='xlsxwriter') as writer:
        all_teams_df.to_excel(writer, index=False)

        # Format the last two columns (Rank Sum and Rank Average) in bold
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        rank_sum_col_idx = len(columns) - 2  # Index for 'Rank Sum'
        rank_avg_col_idx = len(columns) - 1  # Index for 'Rank Average'
        bold_format = workbook.add_format({'bold': True})
        worksheet.set_column(rank_sum_col_idx, rank_avg_col_idx, None, bold_format)

    print("Data saved to all_teams_data.xlsx")


if __name__ == "__main__":
    main()


# import pandas as pd
# import xlwings as xw
#
#
# # Function to load the data from Excel into pandas DataFrames
# def load_data(file_path):
#     # Load Excel data into a dictionary of DataFrames
#     data = pd.read_excel(file_path, sheet_name=None)
#     print(data['Week 4'].columns)
#     for sheet_name, df in data.items():
#         print(f"Sheet: {sheet_name}")
#         print(df.columns)  # This will print column names for each sheet
#     return data
#
#
# def inspect_team_names(stats_data):
#     print("Schedule Team Names:")
#     print(stats_data['Week 4']['Thu Sep 26'].unique())  # Check unique team names in schedule
#
#     for sheet_name, df in stats_data.items():
#         if 'Team' in df.columns:
#             print(f"\n{sheet_name} Team Names:")
#             print(df['Team'].unique())  # Check unique team names in each stats sheet
#
#
# # Function to process a single matchup from the schedule
# def process_matchup(schedule_row, stats_data):
#     team_1, team_2 = parse_teams(schedule_row)
#     # Retrieve stats for both teams from various sheets
#     team_1_stats = retrieve_team_stats(team_1, stats_data)
#     team_2_stats = retrieve_team_stats(team_2, stats_data)
#     # Combine and return stats for both teams
#     return combine_stats(team_1_stats, team_2_stats)
#
#
# # Helper function to parse team names from a schedule row
# def parse_teams(schedule_row):
#     # Extract team names from a row, assuming format like "Team1 @ Team2"
#     teams = schedule_row.split(' @ ')
#     team_1 = teams[0].strip()
#     team_2 = teams[1].strip()
#     return team_1, team_2
#
#
# # Function to retrieve statistics for a specific team
# def retrieve_team_stats(team_name, stats_data):
#     team_name = team_name.strip()  # Remove any extra spaces
#     team_stats = {}
#
#     for sheet_name, df in stats_data.items():
#         if 'Team' in df.columns:
#             df['Team'] = df['Team'].str.strip()  # Clean up team names in the stats sheets
#
#             # Check if the team exists in the current sheet
#             team_row = df[df['Team'] == team_name]
#
#             # Add more checks to handle name variations or abbreviations if needed (e.g., "NY" vs "New York")
#             if team_row.empty:
#                 if team_name == "NY Giants":
#                     team_row = df[df['Team'] == "NY Giants"]
#                 elif team_name == "NY Jets":
#                     team_row = df[df['Team'] == "NY Jets"]
#                 # Add similar cases for other team abbreviations if needed
#
#             if not team_row.empty:
#                 team_stats[sheet_name] = team_row.values[0]
#
#     return team_stats
#
#
# # Function to combine stats for both teams into a single row
# def combine_stats(team_1_stats, team_2_stats):
#     combined = list(team_1_stats.values()) + list(team_2_stats.values())
#     return combined
#
#
# # Function to write the final combined data to Excel
# # Function to write the final combined data to Excel using pandas
# def write_to_excel(output_file, combined_data):
#     # If combined_data is not already a DataFrame, convert it
#     if not isinstance(combined_data, pd.DataFrame):
#         combined_data = pd.DataFrame(combined_data)
#
#     # Write the data to an Excel file
#     combined_data.to_excel(output_file, index=False)
#
#     print(f"Data successfully written to {output_file}")
#
#
# # Main function to orchestrate the flow
# def main():
#     file_path = "NFL Weekly Data.xlsx"
#     output_file = "output_file.xlsx"
#
#     # Load the data from Excel
#     stats_data = load_data(file_path)
#
#     #inspecting names
#     inspect_team_names(stats_data)
#
#     # Assuming we load the schedule from the 'Week 4' sheet
#     schedule = stats_data['Week 4']['Thu Sep 26'].dropna()
#
#     combined_data = []
#     for row in schedule:
#         combined_data.append(process_matchup(row, stats_data))
#
#     # Write the final combined data to Excel
#     write_to_excel(output_file, combined_data)
#
#
# if __name__ == "__main__":
#     main()
