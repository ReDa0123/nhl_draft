from cleverminer import cleverminer
import pandas as pd

stats_df = pd.read_csv('../nhl_player_stats.csv', encoding='unicode_escape')
draft_df = pd.read_csv('../nhl_draft.csv', encoding='unicode_escape')

desired_column = 'PIMPG_CAT'
NEW_COLUMN_NAME = 'FIRST_NHL_SEASON_STAT'

# Get all the first seasons of players
first_seasons = stats_df[stats_df['PLAYER_SEASON_NUMBER'] == 1]

# Add PPG_CAT and SEASON_CAT to the draft dataframe
draft_df = draft_df.assign(**{NEW_COLUMN_NAME: None})
draft_df = draft_df.assign(FIRST_NHL_SEASON_DECADE=None)

# For each player in the first_seasons dataframe, add the PPG and decade of the first season to the draft dataframe
for _, row in first_seasons.iterrows():
    player_id = row['PLAYER_ID']
    draft_df.loc[draft_df['PLAYER_ID'] == player_id, NEW_COLUMN_NAME] = row[desired_column]
    draft_df.loc[draft_df['PLAYER_ID'] == player_id, 'FIRST_NHL_SEASON_DECADE'] = row['SEASON_CAT']

# Get only players with the newly added columns
draft_df = draft_df[draft_df[NEW_COLUMN_NAME].notnull()]
draft_df = draft_df[draft_df['FIRST_NHL_SEASON_DECADE'].notnull()]

# To use rcut onNEW_COLUMN_NAME, we need to make it sortable
categories = ['very low', 'low', 'medium', 'high', 'very high']
sortable_categories = [f'{index}_{value}' for index, value in enumerate(categories)]
draft_df[NEW_COLUMN_NAME] = draft_df[NEW_COLUMN_NAME].replace(categories, sortable_categories)

# Remove players with no position
draft_df = draft_df[draft_df['POSITION'].notnull()]

clm = cleverminer(df=draft_df, proc='4ftMiner',
                  quantifiers={'conf': 0.75, 'Base': 50},
                  ante={
                      'attributes': [
                          {'name': 'HEIGHT_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'WEIGHT_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'NATIONALITY_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'FIRST_NHL_SEASON_DECADE', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'AMATEUR_LEAGUE_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'AVERAGE_JUNIOR_PPG_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'LAST_JUNIOR_YEAR_PPG_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'SHOOTS', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'POSITION', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                      ], 'minlen': 1, 'maxlen': 3, 'type': 'con'},
                  succ={
                      'attributes': [
                          {'name': NEW_COLUMN_NAME, 'type': 'rcut', 'minlen': 1, 'maxlen': 2},
                      ], 'minlen': 1, 'maxlen': 1, 'type': 'con'},
                  )

clm.print_rulelist()
