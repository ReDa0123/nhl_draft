from cleverminer import cleverminer
import pandas as pd

draft_df = pd.read_csv('../nhl_draft.csv', encoding='unicode_escape')

# Filter out not player with no height or weight
draft_df = draft_df[draft_df['HEIGHT_CAT'].notnull()]
draft_df = draft_df[draft_df['WEIGHT_CAT'].notnull()]

# Fill draft round with 100 for undrafted players
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].fillna(100)

# Combine players drafted in round 1, 2 and 3 into one category
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].replace([1, 2, 3], 'EARLY')

# Combine other drafted players into one category
draft_df['DRAFT_ROUND'] = draft_df['DRAFT_ROUND'].replace([4, 5, 6, 7, 8, 9, 10, 100], 'LATE')

# To use sequences, we need to rename the columns
# First code strings into numbers
avg_junior_ppg_cats = ['very low', 'low', 'medium', 'high', 'very high']
weight_cats = ['<75', '75-85', '85-95', '95-105', '105-115', '115-130', 'MAXICHONKER']
replace_avg_ppg = [f'{index}_{value}' for index, value in enumerate(avg_junior_ppg_cats)]
replace_weight = [f'{index}_{value}' for index, value in enumerate(weight_cats)]
draft_df['AVERAGE_JUNIOR_PPG_CAT'] = draft_df['AVERAGE_JUNIOR_PPG_CAT'].replace(avg_junior_ppg_cats, replace_avg_ppg)
draft_df['WEIGHT_CAT'] = draft_df['WEIGHT_CAT'].replace(weight_cats, replace_weight)


# Using the CFMiner procedure from the cleverminer package to find associative rules with base over 50
# and quantifier S_Up = 1 (setting relative min for the second category over 0.5 should also work)
# These player attributes were chosen as candidates for the antecedent: Weight and Height,
# Average PPG in all juniors, Average PPG in last junior season (to get more rules,
# sequence will be used for weight and avg junior ppg categories of max length 2 instead of subset)
# and Nationality. We classify 'being drafted more in the later rounds' as relative number of players in 4+ rounds
# is at least 85 %.
clm = cleverminer(
    df=draft_df,
    target='DRAFT_ROUND',
    proc='CFMiner',
    quantifiers={'S_Up': 1, 'Base': 50, 'RelMax': 0.85},
    cond={
        'attributes': [
            {'name': 'HEIGHT_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'WEIGHT_CAT', 'type': 'seq', 'minlen': 1, 'maxlen': 2},
            {'name': 'AVERAGE_JUNIOR_PPG_CAT', 'type': 'seq', 'minlen': 1, 'maxlen': 2},
            {'name': 'LAST_JUNIOR_YEAR_PPG_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
            {'name': 'NATIONALITY_CAT', 'type': 'subset', 'minlen': 1, 'maxlen': 1},
        ], 'minlen': 1, 'maxlen': 5, 'type': 'con'
    }
)

clm.print_rulelist()
