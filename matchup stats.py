import pandas as pd
import xlwings as xw


# Load the Weekly Schedule DataFrame (scraped from previous code)
def load_weekly_schedule(file_path):
    return pd.read_excel(file_path)


# Load the NFL stats workbook
def load_nfl_stats(file_path):
    return pd.read_excel(file_path, sheet_name=None)


# Function to find the rank of the team in each sheet
def get_team_rank(team_name, nfl_stats_sheets):
    team_ranks = []

    for sheet_name, df in nfl_stats_sheets.items():
        # Check if the team exists in this sheet
        if 'Team' in df.columns:
            team_row = df[df['Team'].str.contains(team_name, na=False, case=False)]
            if not team_row.empty:
                rank_value = team_row['Rank'].values[0]
                team_ranks.append(rank_value)
            else:
                team_ranks.append(None)  # If team not found in this sheet
        else:
            team_ranks.append(None)  # If there's no 'Team' column in this sheet

    return team_ranks


# Build the final DataFrame by iterating over the schedule and nfl_stats
def build_matchup_stats(schedule_df, nfl_stats_sheets):
    final_data = []

    # Iterate over each row in the schedule (each matchup)
    for idx, row in schedule_df.iterrows():
        teams = row['Teams'].split('@')

        if len(teams) != 2:
            print(f"Warning: Skipping malformed matchup in row {idx}: {row['Teams']}")
            continue

        team1 = teams[0].strip()
        team2 = teams[1].strip()

        # Get the rank values for each team
        team1_ranks = get_team_rank(team1, nfl_stats_sheets)
        team2_ranks = get_team_rank(team2, nfl_stats_sheets)

        # Calculate sum and average for team1
        team1_rank_sum = sum([r for r in team1_ranks if r is not None])
        team1_rank_avg = team1_rank_sum / len([r for r in team1_ranks if r is not None])

        # Calculate sum and average for team2
        team2_rank_sum = sum([r for r in team2_ranks if r is not None])
        team2_rank_avg = team2_rank_sum / len([r for r in team2_ranks if r is not None])

        # Append both teams' data into the final list, followed by a blank row
        final_data.append([team1] + team1_ranks + [team1_rank_sum, team1_rank_avg])
        final_data.append([team2] + team2_ranks + [team2_rank_sum, team2_rank_avg])
        final_data.append([''] * (len(team1_ranks) + 3))  # Blank row

    # Build final DataFrame with dynamic column names
    column_names = ['Team'] + [f'Rank_{sheet}' for sheet in nfl_stats_sheets.keys()] + ['Rank Total', 'Rank Average']
    final_df = pd.DataFrame(final_data, columns=column_names)

    return final_df


# Main function to load the data, process it, and export it
def main():
    # Paths to the files
    schedule_file = 'nfl_current_week_schedule.xlsx'  # Replace with your actual path
    stats_file = 'nfl_stats.xlsx'  # Replace with your actual path

    # Load schedule and NFL stats
    schedule_df = load_weekly_schedule(schedule_file)
    nfl_stats_sheets = load_nfl_stats(stats_file)

    # Build the final DataFrame with the matchups and ranks
    final_df = build_matchup_stats(schedule_df, nfl_stats_sheets)

    # Export the final DataFrame to Excel
    final_df.to_excel('nfl_matchup_rankings_with_totals.xlsx', index=False)
    print("Exported matchup rankings with totals to 'nfl_matchup_rankings_with_totals.xlsx'")


if __name__ == "__main__":
    main()
