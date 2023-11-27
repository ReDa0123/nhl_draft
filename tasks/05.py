from cleverminer import cleverminer
import pandas as pd

draft_df = pd.read_csv('../nhl_draft.csv', encoding='unicode_escape')

# Remove players with no position or wrong position
draft_df = draft_df[
    (draft_df['POSITION'].notnull()) &
    (draft_df['POSITION'] != 'W') &
    (draft_df['POSITION'] != 'C; LW') &
    (draft_df['POSITION'] != 'C RW') &
    (draft_df['POSITION'] != 'L') &
    (draft_df['POSITION'] != 'F') &
    (draft_df['POSITION'] != 'Centr')
]

# Categorize draft rounds more and enable sequences
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].fillna(100)
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].replace([1, 2], '0_EARLY')
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].replace([3, 4], '1_MID')
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].replace([5, 6, 7, 8, 9, 10, 100], '2_LATE')

# Fill in height and weight to most common value
draft_df['HEIGHT_CAT'] = draft_df['HEIGHT_CAT'].fillna('185-195')
draft_df['WEIGHT_CAT'] = draft_df['WEIGHT_CAT'].fillna('85-95')

# To use sequences, we need to rename the columns
height_cats = ['<175', '175-185', '185-195', 'GIANT']
weight_cats = ['<75', '75-85', '85-95', '95-105', '105-115', '115-130', 'MAXICHONKER']
replace_height = [f'{index}_{value}' for index, value in enumerate(height_cats)]
replace_weight = [f'{index}_{value}' for index, value in enumerate(weight_cats)]
draft_df['HEIGHT_CAT'] = draft_df['HEIGHT_CAT'].replace(height_cats, replace_height)
draft_df['WEIGHT_CAT'] = draft_df['WEIGHT_CAT'].replace(weight_cats, replace_weight)

# Using the CFMiner procedure from the cleverminer package to find associative rules with base over 50
# We will want to find groups where every position is represented equally +-5 % relative count.
# Attributes chosen: Draft round (seq 1-2), Nationality, Amateur league location, Average junior PPG,
# Height (seq 1-2), Weight (seq 1-2)
clm = cleverminer(
    df=draft_df,
    target='POSITION',
    proc='CFMiner',
    quantifiers={'Base': 50, 'RelMin': 0.15, 'RelMax_leq': 0.25},
    cond={
        'attributes': [
            {'name': 'DRAFT_ROUND', 'type': 'seq', 'minlen': 1, 'maxlen': 2},
            {'name': 'NATIONALITY_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'AMATEUR_LEAGUE_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'AVERAGE_JUNIOR_PPG_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'HEIGHT_CAT', 'type': 'seq', 'minlen': 1, 'maxlen': 2},
            {'name': 'WEIGHT_CAT', 'type': 'seq', 'minlen': 1, 'maxlen': 2},
        ], 'minlen': 1, 'maxlen': 3, 'type': 'con'
    }
)

clm.print_rulelist()
