"""
Sources of data:
https://www.kaggle.com/datasets/mjavon/elite-prospects-hockey-stats-player-data/data (player_stats.csv + player_dim.csv)
https://www.kaggle.com/datasets/mattop/nhl-draft-hockey-player-data-1963-2022/data (nhldraft.csv)
"""

import pandas as pd
import numpy as np

# Column name constants.
PLAYER_ID = 'PLAYER_ID'
PLAYER_NAME = 'PLAYER_NAME'
LEAGUE = 'LEAGUE'
DRAFT_YEAR = 'draft_year'
DRAFT_TEAM = 'draft_team'
AMATEUR_LEAGUE = 'amateur_league'
GAMES_PLAYED = 'games_played'
OTHER = 'other'
DRAFT_ROUND = 'draft_round'
LEAGUE_YEAR = 'LEAGUE_YEAR'
PPG = 'PPG'

categories = ['very low', 'low', 'medium', 'high', 'very high']
per_game_categories_intervals = [-np.inf, 0.2, 0.4, 0.6, 0.8, np.inf]
games_played_categories_intervals = [-np.inf, 100, 300, 500, 700, np.inf]

# Read original CSV files.
player_stats_df = pd.read_csv('player_stats.csv', encoding='unicode_escape')
player_dim_df = pd.read_csv('player_dim.csv', encoding='unicode_escape')
draft_info_df = pd.read_csv('nhldraft.csv')

# Copy original stats
player_stats_original_df = player_stats_df.copy()

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

# Rename nationality column to make it unique and player name column to make it consistent
draft_info_df = draft_info_df.rename(columns={'nationality': 'nationality_abbr', 'player': PLAYER_NAME})

# Remove draft info rows with players drafted after 2018/19 season and players drafted before 1978/79 season.
draft_info_df = draft_info_df[draft_info_df['year'] < 2019]
draft_info_df = draft_info_df[draft_info_df['year'] >= 1978]

# Add draft round column (in today's number of teams)
draft_info_df[DRAFT_ROUND] = draft_info_df.apply(lambda row: (row['overall_pick'] - 1) // 32 + 1, axis=1)

# Join player dim and draft info based on PLAYER_NAME.
# Rename player to PLAYER_NAME in draft info first.
# We will keep both non-mergable columns in the joined df.
# If the player was not drafted, the draft info will be NaN.
# If the player has been drafted and has not played in the NHL, the player dim() info will be NaN.
# Note: We will not resolve an issue where multiple players have the same name as it is very unlikely and would require
# a bit of effort to resolve (from the top of my head there are two players named Sebastian Aho.)
joined_df = draft_info_df.merge(player_dim_df, on=PLAYER_NAME, how='outer')
# Rename draft year and draft team columns
joined_df = joined_df.rename(columns={'year': DRAFT_YEAR, 'team': DRAFT_TEAM})

# Add amateur league
joined_df[AMATEUR_LEAGUE] = joined_df['amateur_team'].str.extract(r'\((.*?)\)', expand=False)

# Take only the primary position and nationality
joined_df['position'] = joined_df['position'].str.replace(r'\/.+', '', regex=True)
joined_df['NATIONALITY'] = joined_df['NATIONALITY'].str.replace(r'\/.+', '', regex=True)

# Categorize statistical columns for stats df
# First let's add goals per game, assists per game and penalty minutes per game
player_stats_df['GPG'] = player_stats_df['G'] / player_stats_df['GP']
player_stats_df['APG'] = player_stats_df['A'] / player_stats_df['GP']
player_stats_df['PIMPG'] = player_stats_df['PIM'] / player_stats_df['GP']

# Now let's categorize the newly added columns and points per game
player_stats_df['GPG_CAT'] = pd.cut(player_stats_df['GPG'], per_game_categories_intervals, labels=categories)
player_stats_df['APG_CAT'] = pd.cut(player_stats_df['APG'], per_game_categories_intervals, labels=categories)
player_stats_df['PIMPG_CAT'] = pd.cut(player_stats_df['PIMPG'], per_game_categories_intervals, labels=categories)
player_stats_df['PPG_CAT'] = pd.cut(player_stats_df[PPG], per_game_categories_intervals, labels=categories)

# Categorize plus minus and games played as quantiles
player_stats_df['PLUS_MINUS_CAT'] = pd.qcut(player_stats_df['+/-'], 5, labels=categories)
player_stats_df['GP_CAT'] = pd.qcut(player_stats_df['GP'], 5, labels=categories)


# Categorize season
def categorize_season(row):
    first_year = int(str(row[LEAGUE_YEAR])[:4])
    if first_year < 1990:
        return '80s'
    if first_year < 2000:
        return '90s'
    if first_year < 2010:
        return '00s'
    if first_year < 2020:
        return '10s'
    return '20s'


player_stats_df['SEASON_CAT'] = player_stats_df.apply(categorize_season, axis=1)


# Let's categorize seasons also if they are pre or in the salary cap era
def is_in_cap_era(row):
    first_year = int(str(row[LEAGUE_YEAR])[:4])
    if first_year < 2005:
        return 'PRE_CAP_ERA'
    return 'IN_CAP_ERA'


player_stats_df['IS_IN_CAP_ERA'] = player_stats_df.apply(is_in_cap_era, axis=1)

# Add season number to players
player_stats_df['PLAYER_SEASON_NUMBER'] = player_stats_df.groupby(PLAYER_ID).cumcount() + 1

# Categorize statistical columns for draft df
# First let's add points per game, goals per game, assists per game and penalty minutes per game
joined_df[PPG] = joined_df['points'] / joined_df[GAMES_PLAYED]
joined_df['GPG'] = joined_df['goals'] / joined_df[GAMES_PLAYED]
joined_df['APG'] = joined_df['assists'] / joined_df[GAMES_PLAYED]
joined_df['PIMPG'] = joined_df['penalties_minutes'] / joined_df[GAMES_PLAYED]

# Now let's categorize the newly added columns
joined_df['PPG_CAT'] = pd.cut(joined_df[PPG], per_game_categories_intervals, labels=categories)
joined_df['GPG_CAT'] = pd.cut(joined_df['GPG'], per_game_categories_intervals, labels=categories)
joined_df['APG_CAT'] = pd.cut(joined_df['APG'], per_game_categories_intervals, labels=categories)
joined_df['PIMPG_CAT'] = pd.cut(joined_df['PIMPG'], per_game_categories_intervals, labels=categories)

# Categorize plus minus, point shares and games played as quantiles
joined_df['PLUS_MINUS_CAT'] = pd.qcut(joined_df['plus_minus'], 5, labels=categories)
joined_df['POINT_SHARES_CAT'] = pd.qcut(joined_df['point_shares'], 5, labels=categories)
joined_df['GAMES_PLAYED_CAT'] = pd.qcut(joined_df[GAMES_PLAYED], 5, labels=categories)

# Categorize nationality based on nationality and nationality_abbr
# The most common nationalities are CAN, USA, SWE, RUS, CZE, FIN, SVK, SUI and GER - the others will be categorized as
# OTHER
nationalities = {
    'CA': 'Canada',
    'US': 'USA',
    'SE': 'Sweden',
    'RU': 'Russia',
    'CZ': 'CzechRep.',
    'FI': 'Finland',
    'SK': 'Slovakia',
    'CH': 'Switzerland',
    'DE': 'Germany'
}


def categorize_nationality(row):
    nat = row['NATIONALITY']
    nat_abbr = row['nationality_abbr']
    if nat in nationalities.values():
        return nat
    elif nat_abbr in nationalities.keys():
        return nationalities[nat_abbr]
    else:
        return OTHER


joined_df['NATIONALITY_CAT'] = joined_df.apply(categorize_nationality, axis=1)

# Categorize amateur league
# First lets create categories for the most common leagues
amateur_leagues = {
    'europe': (
        'Sweden', 'Sweden Jr.', 'Finland', 'Finland Jr.', 'Finaland Jr.', 'Czechoslovakia', 'Sweden-2', 'Czech',
        'Czech Jr.',
        'Finland-2', 'Czech-2', 'Slovakia', 'Slovakia Jr.', 'Swiss Jr.', 'Sweden-3', 'Swiss', 'Swiss-2', 'France',
        'Denmark', 'Germany', 'Germany-2', 'Germany Jr.', 'Norway', 'DEL', 'Slovakia-2', 'Belarus', 'Austria', 'Latvia',
    ),
    'north_america': (
        'OHL', 'WHL', 'QMJHL', 'WCHL', 'WCHA', 'USHL', 'ECAC', 'OHA-Jr.', 'OMJHL', 'CMJHL', 'COJHL', 'CCHA',
        'USDP/USHL', 'High-CT', 'AJHL', 'NAHL', 'Big Ten', 'NCHC', 'CCHL', 'OJHL', 'H-East', 'BCHL',
        'USMAAA', 'Ohio', 'WOHL', 'AHL', 'USDP/NAHL', 'CJHL', 'OPJHL', 'EJHL', 'IHL', 'WHA', 'SJHL', 'QJAHL', 'NEJHL',
        'MidJHL', 'MetJBHL', 'CIAU', 'BCJHL', 'SMAAAHL', 'OPJAHL', 'NOJHL', 'NCAA-Ind.', 'MetJAHL', 'MWJHL', 'MJHL',
    ),
    'russia': ('Russia', 'Russia-2', 'Russia-3', 'Russia Jr.', 'Soviet', 'Soviet-2', 'Soviet-3'),
}


def categorize_amateur_league(row):
    for area, leagues in amateur_leagues.items():
        if row[AMATEUR_LEAGUE] in leagues:
            return area
    if str(row[AMATEUR_LEAGUE]).startswith('High'):
        return 'north_america'
    return 'NOT_DRAFTED' if str(row[AMATEUR_LEAGUE]) == 'nan' else OTHER


joined_df['AMATEUR_LEAGUE_CAT'] = joined_df.apply(categorize_amateur_league, axis=1)


# Add ppg from juniors (last year and average) to draft df
def get_junior_stats(row):
    if str(row[PLAYER_ID]) == 'nan':
        return 0, 0

    seasons_by_player = player_stats_original_df[player_stats_original_df[PLAYER_ID] == row[PLAYER_ID]].sort_values(
        by=LEAGUE_YEAR
    )
    first_nhl_season_year = seasons_by_player[seasons_by_player[LEAGUE] == 'NHL'].iloc[0][LEAGUE_YEAR]
    non_nhl_seasons = seasons_by_player[seasons_by_player[LEAGUE_YEAR] < first_nhl_season_year]
    if non_nhl_seasons.empty:
        return 0, 0
    average_ppg_in_junior = non_nhl_seasons[PPG].mean()
    return non_nhl_seasons.iloc[-1][PPG], average_ppg_in_junior


joined_df['LAST_JUNIOR_YEAR_PPG'] = joined_df.apply(lambda row: get_junior_stats(row)[0], axis=1)
joined_df['AVERAGE_JUNIOR_PPG'] = joined_df.apply(lambda row: get_junior_stats(row)[1], axis=1)

# Add draft info to player stats
player_stats_df = player_stats_df.merge(
    joined_df[[DRAFT_YEAR, 'overall_pick', DRAFT_TEAM, AMATEUR_LEAGUE, PLAYER_ID, 'AMATEUR_LEAGUE_CAT', DRAFT_ROUND]],
    on=PLAYER_ID,
    how='left'
)

# Normalize column names in dfs
joined_df.columns = joined_df.columns.str.upper()
player_stats_df.columns = player_stats_df.columns.str.upper()

# Export to CSV.
joined_df.to_csv('nhl_draft.csv', index=False)
player_stats_df.to_csv('nhl_player_stats.csv', index=False)
