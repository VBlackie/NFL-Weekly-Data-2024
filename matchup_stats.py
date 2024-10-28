import pandas as pd
import re
from datetime import datetime
import logging
from validation_functions import run_validations

# Set up logging
logging.basicConfig(
    filename='nfl_pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


# Load the Weekly Schedule DataFrame (scraped from previous code)
def load_weekly_schedule(file_path):
    logging.info(f"Loading weekly schedule from {file_path}")
    return pd.read_excel(file_path)


# Load the NFL stats workbook
def load_nfl_stats(file_path):
    logging.info(f"Loading NFL stats from {file_path}")
    return pd.read_excel(file_path, sheet_name=None)


# Function to find the rank of the team in each sheet
def get_team_rank(team_name, nfl_stats_sheets):
    team_ranks = []
    for sheet_name, df in nfl_stats_sheets.items():
        # Validate the data and check for the required 'Team' column
        if 'Team' in df.columns and run_validations(df, sheet_name, required_columns=['Team', 'Rank']):
            team_row = df[df['Team'].str.contains(team_name, na=False, case=False)]
            rank_value = team_row['Rank'].values[0] if not team_row.empty else None
            team_ranks.append(rank_value)
        else:
            team_ranks.append(None)  # If team not found in this sheet
    return team_ranks


# Build the final DataFrame by iterating over the schedule and nfl_stats
def build_matchup_stats(schedule_df, nfl_stats_sheets):
    final_data = []
    # Validate schedule DataFrame
    if not run_validations(schedule_df, "Weekly Schedule", required_columns=['Teams']):
        logging.error("Validation failed for schedule_df.")
        return pd.DataFrame()  # Return an empty DataFrame if validation fails

    # Iterate over each row in the schedule (each matchup)
    for idx, row in schedule_df.iterrows():
        teams = re.split(r'\s*@\s*|\s*vs\.\s*|\s*vs\s*', row['Teams'])
        logging.info(f"Row {idx}: Splitting '{row['Teams']}' resulted in {teams}")

        if len(teams) != 2:
            logging.warning(f"Skipping malformed matchup in row {idx}: {row['Teams']}")
            continue

        team1, team2 = teams[0].strip(), teams[1].strip()
        team1_ranks, team2_ranks = get_team_rank(team1, nfl_stats_sheets), get_team_rank(team2, nfl_stats_sheets)

        # Calculate sum and average for each team
        team1_rank_sum = sum(r for r in team1_ranks if r is not None)
        team1_rank_count = len([r for r in team1_ranks if r is not None])
        team1_rank_avg = team1_rank_sum / team1_rank_count if team1_rank_count > 0 else None
        team2_rank_sum = sum(r for r in team2_ranks if r is not None)
        team2_rank_count = len([r for r in team2_ranks if r is not None])
        team2_rank_avg = team2_rank_sum / team2_rank_count if team2_rank_count > 0 else None

        match_id = f'Match {idx + 1}'
        final_data.extend([
            [match_id, team1] + team1_ranks + [team1_rank_sum, team1_rank_avg],
            [match_id, team2] + team2_ranks + [team2_rank_sum, team2_rank_avg]
        ])

    column_names = ['Match ID', 'Team'] + [f'Rank_{sheet}' for sheet in nfl_stats_sheets.keys()] + ['Rank Total',
                                                                                                    'Rank Average']
    final_df = pd.DataFrame(final_data, columns=column_names)

    return final_df


# Function to save output with and without date signature
def save_output_with_date(final_df):
    current_date = datetime.now().strftime('%Y-%m-%d')
    final_df.to_excel(f'nfl_output_{current_date}.xlsx', index=False)
    final_df.to_excel('nfl_output.xlsx', index=False)
    logging.info(f"Files saved: 'nfl_output_{current_date}.xlsx' and 'nfl_output.xlsx'")


# Main function to load the data, process it, and export it
def main():
    schedule_file = 'nfl_current_week_schedule.xlsx'
    stats_file = 'nfl_stats.xlsx'

    # Load and validate schedule and NFL stats
    schedule_df = load_weekly_schedule(schedule_file)
    nfl_stats_sheets = load_nfl_stats(stats_file)

    # Build the final DataFrame with the matchups and ranks
    final_df = build_matchup_stats(schedule_df, nfl_stats_sheets)

    # Export the final DataFrame to Excel
    try:
        if not final_df.empty:
            save_output_with_date(final_df)
            logging.info("ETL matchup_stats pipeline completed successfully.")
        else:
            logging.error("No data to save; final DataFrame is empty.")
    except Exception as e:
        logging.error(f"ETL matchup_stats pipeline failed: {e}")


if __name__ == "__main__":
    main()
