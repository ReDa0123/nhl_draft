import pandas as pd
import requests as req
from bs4 import BeautifulSoup
import time
import re

PLAYER_URL = 'PLAYER_URL'
NOT_DRAFTED = 'NOT_DRAFTED'
PLAYER_ID = 'PLAYER_ID'
LEAGUE = 'LEAGUE'

# Open the CSV file, read it into a DataFrame and get the URLs.
df = pd.read_csv('player_stats.csv', encoding='unicode_escape')
# Filter out the duplicate URLs and select only NHL players.
df = df.loc[df[LEAGUE] == 'NHL'].drop_duplicates(subset=[PLAYER_URL])
print(len(df))

# Create a new list for the draft information.
# Columns will be ['PLAYER_ID', 'YEAR_DRAFTED', 'ROUND_DRAFTED', 'OVERALL_DRAFTED', 'DRAFTED_BY']
draft_data = []


def extract_draft_info(draft_string: str) -> dict[str, str | int]:
    pattern = r'(\d{4}) round (\d+) #(\d+) overall by (.+)'
    match = re.match(pattern, draft_string)

    # The draft string should always match the pattern because we already checked if the draft element exists.
    year_drafted = int(match.group(1))
    round_drafted = int(match.group(2))
    overall_drafted = int(match.group(3))
    drafted_by = match.group(4)

    return dict(
        YEAR_DRAFTED=year_drafted,
        ROUND_DRAFTED=round_drafted,
        OVERALL_DRAFTED=overall_drafted,
        DRAFTED_BY=drafted_by
    )


def add_draft_info() -> None:
    global draft_data, df
    for _, row in df.iterrows():
        url = row[PLAYER_URL]
        player_id = row[PLAYER_ID]
        response = req.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find the draft string using the following XPath expression:
        # //a[starts-with(@href,'https://www.eliteprospects.com/draft/nhl-entry-draft/')]
        draft_el = soup.find(
            'a',
            href=lambda href: href and href.strip().startswith('https://www.eliteprospects.com/draft/nhl-entry-draft/')
        )
        # If that element is not found, the player was not drafted. Continue to the next player.
        if draft_el is None:
            draft_data.append(dict(
                PLAYER_ID=player_id,
                YEAR_DRAFTED=NOT_DRAFTED,
                ROUND_DRAFTED=NOT_DRAFTED,
                OVERALL_DRAFTED=NOT_DRAFTED,
                DRAFTED_BY=NOT_DRAFTED
            ))
            continue

        draft_str = draft_el.text.strip()
        draft_info = extract_draft_info(draft_str)
        # Add the player ID to the draft info.
        draft_info[PLAYER_ID] = player_id
        draft_data.append(draft_info)
        # Sleep for 6 seconds to avoid getting blocked. This process should take approximately 6-7 hours.
        time.sleep(6)


add_draft_info()

# Create a new DataFrame from the draft data and save it to a CSV file.
draft_df = pd.DataFrame(draft_data)
draft_df.to_csv('draft_data.csv', index=False)

print('Done!')
