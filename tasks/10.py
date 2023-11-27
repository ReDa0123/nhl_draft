from cleverminer import cleverminer
import pandas as pd

stats_df = pd.read_csv('../nhl_player_stats.csv', encoding='unicode_escape')
draft_df = pd.read_csv('../nhl_draft.csv', encoding='unicode_escape')

# What stat to use for the comparison
desired_stat = 'PPG'

season_of_players_grouped = stats_df.groupby('PLAYER_ID')

for player_id, player_stats in season_of_players_grouped:
    # Initialize variables
    first_three_season_stats = 0
    first_three_season_count = 0
    four_to_six_season_stats = 0
    four_to_six_season_count = 0
    other_stats = 0
    other_count = 0
    # We only want players that have played at least 4 seasons
    if len(player_stats) < 4:
        continue

    # Calculate the average PPG for the first three seasons, the next three seasons and the rest
    for _, row in player_stats.iterrows():
        season_number = row['PLAYER_SEASON_NUMBER']
        if season_number <= 3:
            first_three_season_stats += row[desired_stat]
            first_three_season_count += 1
        elif 4 <= season_number <= 6:
            four_to_six_season_stats += row[desired_stat]
            four_to_six_season_count += 1
        else:
            other_stats += row[desired_stat]
            other_count += 1

    # Divide by the number of seasons to get the average
    first_three_season_stats /= first_three_season_count
    if four_to_six_season_count != 0:
        four_to_six_season_stats /= four_to_six_season_count
    if other_count != 0:
        other_stats /= other_count

    # Add the new column to the draft dataframe
    gets_worse = first_three_season_stats >= four_to_six_season_stats >= other_stats
    draft_df.loc[draft_df['PLAYER_ID'] == player_id, 'GETS_WORSE'] = str(gets_worse)

# Get only players with the newly added column
draft_df = draft_df[draft_df['GETS_WORSE'].notnull()]

# Categorize draft round more
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].fillna(999)
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].replace([1, 2, 3], 'EARLY')
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].replace([4, 5, 6, 7, 8, 9, 10, 999], 'LATE')

# Using the 4ftMiner procedure from the cleverminer package to find associative rules with confidence above 0.6
# These player attributes were chosen as candidates for the antecedent: Weight, Height,
# Average PPG in juniors, Nationality, Amateur league location, Draft round (Lat/Early)
# Succedents: Gets worse
clm = cleverminer(df=draft_df, proc='4ftMiner',
                  quantifiers={'conf': 0.6, 'Base': 10},
                  ante={
                      'attributes': [
                          {'name': 'HEIGHT_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'WEIGHT_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'AVERAGE_JUNIOR_PPG_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'NATIONALITY_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'AMATEUR_LEAGUE_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'DRAFT_ROUND', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                      ], 'minlen': 1, 'maxlen': 2, 'type': 'con'},
                  succ={
                      'attributes': [
                          {'name': 'GETS_WORSE', 'type': 'one', 'value': 'True'},
                      ], 'minlen': 1, 'maxlen': 1, 'type': 'con'},
                  )

clm.print_rulelist()
