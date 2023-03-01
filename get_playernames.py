import requests
from bs4 import BeautifulSoup


def fetch_playerlist():
    """
        Fetches a list of player names from the Wikipedia page for the 2022 FIFA World Cup squads.

        Returns:
            set: A set containing the individual tokens from the names of all players listed on the page.
        """
    url = "https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_squads"

    player_list = []

    html_content = requests.get(url).content
    # Parse HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    cells = soup.find_all('th')
    for cell in cells:
        name = cell.get('data-sort-value')
        if name is None:
            continue
        elif "," in name:
            name_tokens = name.split(", ")
            player_list.extend(name_tokens)
        else:
            name_tokens = name.split()
            player_list.extend(name_tokens)

    return [n.lower() for n in set(player_list)]

# print(fetch_playerlist())
