from cleverminer import cleverminer
import pandas as pd

draft_df = pd.read_csv('../nhl_draft.csv', encoding='unicode_escape')

# Filter out not drafted players
draft_df = draft_df[draft_df['PPG_CAT'].notnull()]
draft_df = draft_df[draft_df['HEIGHT_CAT'].notnull()]
draft_df = draft_df[draft_df['WEIGHT_CAT'].notnull()]

# Using the 4ftMiner procedure from the cleverminer package to find associative rules with confidence above 0.5
# These player attributes were chosen as candidates for the antecedent: Weight, Height,
# Average PPG in juniors, Average PPG in last junior season
# All were categorized
# Succedents: PPG, point shares and +/- were chosen as candidates for the successor
clm = cleverminer(df=draft_df, proc='4ftMiner',
                  quantifiers={'conf': 0.45, 'Base': 80},
                  ante={
                      'attributes': [
                          {'name': 'HEIGHT_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'WEIGHT_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'LAST_JUNIOR_YEAR_PPG_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'AVERAGE_JUNIOR_PPG_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'NATIONALITY_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                          {'name': 'AMATEUR_LEAGUE_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
                      ], 'minlen': 1, 'maxlen': 2, 'type': 'con'},
                  succ={
                      'attributes': [
                          {'name': 'DRAFT_ROUND', 'type': 'one', 'value': 1},
                          {'name': 'DRAFT_ROUND', 'type': 'one', 'value': 2},
                          {'name': 'DRAFT_ROUND', 'type': 'one', 'value': 3},
                      ], 'minlen': 1, 'maxlen': 1, 'type': 'con'},
                  )
clm.print_rulelist()
