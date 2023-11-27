from cleverminer import cleverminer
import pandas as pd

draft_df = pd.read_csv('../nhl_draft.csv', encoding='unicode_escape')

# Filter out players with no PPG (did not play in NHL)
draft_df = draft_df[draft_df['PPG_CAT'].notnull()]

# Categorize draft rounds
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].fillna(123)
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].replace([1, 2, 3], 'EARLY')
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].replace([4, 5, 6, 7, 8, 9, 10, 123], 'LATE')

# Fill missing height and weight with most common values
draft_df['HEIGHT_CAT'] = draft_df['HEIGHT_CAT'].fillna('185-195')
draft_df['WEIGHT_CAT'] = draft_df['WEIGHT_CAT'].fillna('85-95')

# To use cuts we need to sort PPG_CAT
categories = ['very low', 'low', 'medium', 'high', 'very high']
sortable_categories = [f'{index}_{value}' for index, value in enumerate(categories)]
draft_df['PPG_CAT'] = draft_df['PPG_CAT'].replace(categories, sortable_categories)

# Using the SD4ftMiner procedure from the cleverminer package to find associative rules with base over 25 (both)
# Confidence ratio of 2.0 and absolute confidence difference of 0.13
# Chosen antecedents: Nationality, Position, Penalty minutes per game, +/- per game, Amateur league location,
# Average PPG in juniors, Weight, Height
# Succedents: PPG (high + very high)
# Groups of Draft round Early and Late
clm = cleverminer(
    df=draft_df,
    proc='SD4ftMiner',
    quantifiers={'Base1': 25, 'Base2': 25, 'Ratioconf': 2.0, 'Deltaconf': 0.13},
    ante={
        'attributes': [
            {'name': 'NATIONALITY_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'POSITION', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'PIMPG_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'PLUS_MINUS_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'AMATEUR_LEAGUE_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'AVERAGE_JUNIOR_PPG_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'HEIGHT_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'WEIGHT_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
        ], 'minlen': 1, 'maxlen': 3, 'type': 'con',
    },
    succ={
        'attributes': [
            {'name': 'PPG_CAT', 'type': 'rcut', 'minlen': 1, 'maxlen': 2},
        ], 'minlen': 1, 'maxlen': 1, 'type': 'con',
    },
    frst={
        'attributes': [
            {'name': 'DRAFT_ROUND', 'type': 'one', 'value': 'EARLY'},
        ], 'minlen': 1, 'maxlen': 1, 'type': 'con',
    },
    scnd={
        'attributes': [
            {'name': 'DRAFT_ROUND', 'type': 'one', 'value': 'LATE'},
        ], 'minlen': 1, 'maxlen': 1, 'type': 'con',
    },
)

clm.print_rulelist()
