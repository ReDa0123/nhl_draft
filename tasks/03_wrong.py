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
                  quantifiers={'conf': 0.2, 'Base': 20},
                  ante={
                      'attributes': [
                          {'name': 'DRAFT_ROUND', 'type': 'one', 'value': 4},
                          {'name': 'DRAFT_ROUND', 'type': 'one', 'value': 5},
                          {'name': 'DRAFT_ROUND', 'type': 'one', 'value': 6},
                          {'name': 'DRAFT_ROUND', 'type': 'one', 'value': 7},
                      ], 'minlen': 1, 'maxlen': 2, 'type': 'con'},
                  succ={
                      'attributes': [
                          {'name': 'PPG_CAT', 'type': 'one', 'value': 'very high'},
                          {'name': 'PPG_CAT', 'type': 'one', 'value': 'high'},
                         {'name': 'PPG_CAT', 'type': 'one', 'value': 'medium'},
                         ], 'minlen': 1, 'maxlen': 1, 'type': 'con'},
                  )
clm.print_rulelist()
