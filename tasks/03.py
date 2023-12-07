from cleverminer import cleverminer
import pandas as pd

draft_df = pd.read_csv('../nhl_draft.csv', encoding='unicode_escape')

# Get only players drafted in 4th or later round (or undrafted)
# First fill the NaN values with 100
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].fillna(100)
draft_df = draft_df[draft_df['DRAFT_ROUND'] >= 4]

# Fill missing height and weight with most common values
draft_df['HEIGHT_CAT'] = draft_df['HEIGHT_CAT'].fillna('185-195')
draft_df['WEIGHT_CAT'] = draft_df['WEIGHT_CAT'].fillna('85-95')

# Get only players with PPG
draft_df = draft_df[draft_df['PPG_CAT'].notnull()]

# Using the 4ftMiner procedure from the cleverminer package to find associative rules with confidence above 0.5
# These player attributes were chosen as candidates for the antecedent: Weight, Height,
# Average PPG in juniors, Average PPG in last junior season, Amateur team location, Shoots (L/R), Nationality
# Succedents: PPG with values very high and high
clm = cleverminer(df=draft_df, proc='4ftMiner',
                  quantifiers={'conf': 0.5, 'Base': 10},
                  ante={
                      'attributes': [
                          {'name': 'HEIGHT_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'WEIGHT_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'LAST_JUNIOR_YEAR_PPG_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'AVERAGE_JUNIOR_PPG_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'AMATEUR_LEAGUE_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'SHOOTS', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'NATIONALITY_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                      ], 'minlen': 1, 'maxlen': 3, 'type': 'con'},
                  succ={
                      'attributes': [
                          {'name': 'PLUS_MINUS_CAT', 'type': 'one', 'value': 'very high'},
                          {'name': 'PLUS_MINUS_CAT', 'type': 'one', 'value': 'high'},
                      ], 'minlen': 1, 'maxlen': 2, 'type': 'con'},
                  )

clm.print_rulelist()
