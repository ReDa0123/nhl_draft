"""
Sources of data:
https://www.kaggle.com/datasets/mjavon/elite-prospects-hockey-stats-player-data/data (player_stats.csv + player_dim.csv)
https://www.kaggle.com/datasets/mattop/nhl-draft-hockey-player-data-1963-2022/data (nhldraft.csv)
"""

import pandas as pd

# Column name constants.
PLAYER_ID = 'PLAYER_ID'
PLAYER_NAME = 'PLAYER_NAME'
LEAGUE = 'LEAGUE'
DRAFT_YEAR = 'draft_year'
DRAFT_TEAM = 'draft_team'

# Read original CSV files.
player_stats_df = pd.read_csv('player_stats.csv', encoding='unicode_escape')
player_dim_df = pd.read_csv('player_dim.csv', encoding='unicode_escape')
draft_info_df = pd.read_csv('nhldraft.csv')

# Filter out non-NHL players from stats.
player_stats_df = player_stats_df.loc[player_stats_df[LEAGUE] == 'NHL']

# Filter out non-NHL players from dim.
player_dim_df = player_dim_df[player_dim_df[PLAYER_ID].isin(player_stats_df[PLAYER_ID])]

# Remove position from the player stats player name column.
player_stats_df[PLAYER_NAME] = player_stats_df[PLAYER_NAME].str.replace(r'\s*\(.+\)\s*', '', regex=True)

# Add full name to the player dim df from player stats df.
player_dim_df = player_dim_df.merge(
    player_stats_df.drop_duplicates(subset=[PLAYER_ID])[[PLAYER_ID, PLAYER_NAME]],
    on=PLAYER_ID
)

# Drop unwanted columns
player_dim_df = player_dim_df.drop(columns=[
    'ROW_ID',
    'FIRST_NAME',
    'LAST_NAME',
    'DRAFT_YEAR',
    'DRAFT_ROUND',
    'DRAFT_OVERALL',
    'CONTRACT_THRU',
    'PLACE_OF_BIRTH',  # Nationality is sufficient
], axis=1)
player_stats_df = player_stats_df.drop(columns=[
    'ROW_ID',
    LEAGUE,
    'PLAYER_URL',
    'FIRST_NAME',
    'LAST_NAME',
    'SECONDARY_POS',
], axis=1)
draft_info_df = draft_info_df.drop(columns=[
    'id',  # Note: Nationality is in both dfs, but we want to preserve it for players who have not played in the NHL.
], axis=1)

# Remove draft info rows with players drafted after 2018/19 season.
draft_info_df = draft_info_df[draft_info_df['year'] < 2019]

# Join player dim and draft info based on PLAYER_NAME.
# Rename player to PLAYER_NAME in draft info first.
# We will keep both non-mergable columns in the joined df.
# If the player was not drafted, the draft info will be NaN.
# If the player has been drafted and has not played in the NHL, the player dim() info will be NaN.
# Note: We will not resolve an issue where multiple players have the same name as it is very unlikely and would require
# a bit of effort to resolve (from the top of my head there are two players named Sebastian Aho.)
draft_info_df = draft_info_df.rename(columns={'player': PLAYER_NAME})
joined_df = draft_info_df.merge(player_dim_df, on=PLAYER_NAME, how='outer')
# Rename draft year and draft team columns
joined_df = joined_df.rename(columns={'year': DRAFT_YEAR, 'team': DRAFT_TEAM})

# Add draft info to player stats
player_stats_df = player_stats_df.merge(
    joined_df[[DRAFT_YEAR, 'overall_pick', DRAFT_TEAM, 'amateur_team', PLAYER_ID]],
    on=PLAYER_ID,
    how='left'
)

# Export to CSV.
joined_df.to_csv('nhl_draft.csv', index=False)
player_stats_df.to_csv('nhl_player_stats.csv', index=False)
