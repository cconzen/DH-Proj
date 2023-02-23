from TheGuardian_credentials import api_key
import requests
import json
import os
from bs4 import BeautifulSoup


def soup_cleanse(html):
    """
    Cleans up an HTML string by removing specified tags.

    :param html: A string containing HTML code to be cleaned.
    :return: A string containing the cleaned HTML code.
    """
    to_decompose = ['figure', 'span', 'aside']
    to_unwrap = ['a', 'div', 'time', 'strong', 'em', 'bold', 'br', 'li',
                 'ol', 'ul', 's', 'sup', 'h2', 'blockquote', 'p']
    try:
        soup = BeautifulSoup(html, 'html.parser')
    except:
        return ''

    [x.decompose() for tag in to_decompose for x in soup.find_all(tag)]
    [x.unwrap() for tag in to_unwrap for x in soup.find_all(tag)]

    return str(soup)


if not os.path.exists("guardian_articles"):
    os.makedirs("guardian_articles")

base_url = "https://content.guardianapis.com/"
# parameters
query = 'qatar%20world%20cup'
from_date = '2022-02-22'
page_size = 200
show_fields = "body"

# iterating 15 times, 200 articles per page
for page_number in range(1, 16):
    final_url = f"{base_url}search?page-size={page_size}&page={page_number}" \
                f"&from-date={from_date}&q={query}&show-fields={show_fields}&api-key={api_key}"

    # perform the request and print the query
    r = requests.get(url=final_url, params={})
    print(final_url, '\t')

    # output the responses to a file
    Guardian = json.loads(r.text)

    for i in range(len(Guardian['response']['results'])):
        Guardian['response']['results'][i]['fields']['body'] = soup_cleanse(
            Guardian['response']['results'][i]['fields']['body'])

    with open(f'guardian_articles/Guardian_page_{page_number}.json', 'w') as outfile:
        json.dump(Guardian, outfile, indent=4)