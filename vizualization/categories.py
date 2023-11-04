import pandas_cat as pc
import pandas as pd

draft_df = pd.read_csv('../nhl_draft.csv', encoding='unicode_escape')

# Prepare the category profiles
profiles = pc.pandas_cat.profile(df=draft_df, dataset_name="NHL", opts={"auto_prepare": True})
