import nltk

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from string import punctuation
import pandas as pd
import os
import json
from collections import Counter

from get_playernames import fetch_playerlist


def preprocess(newspaper, csv=False):
    """
        Preprocesses text data from JSON files for three different newspapers (The Times, The Sun, and The Guardian),
        including tokenisation, removal of stopwords, punctuation rare tokens and player names, part-of-speech tagging,
        and lemmatisation.
        Returns a Pandas DataFrame containing the preprocessed data.

        Parameters:
        -----------
        newspaper : str, default="sun"
            Name of the newspaper to preprocess data for. Must be one of "times", "sun", or "guardian".
        csv :  bool, default=False
            If True, saves the resulting DataFrame to a CSV file. Defaults to False.
        Raises:
        -------
        ValueError:
            If the 'newspaper' argument is not a string or is not one of the supported newspapers.

        Returns:
        --------
        pandas.DataFrame:
            DataFrame containing the preprocessed text data. The DataFrame has columns for the original article content,
            the preprocessed text, and additional columns for the sentences, tokens, part-of-speech tags, and lemmas.
    """

    if not isinstance(newspaper, str):
        raise ValueError('newspaper argument must be a string')
    newspaper = newspaper.lower()
    if newspaper not in ["times", "sun", "guardian"]:
        raise ValueError('newspaper argument must be one of "times", "sun", or "guardian"')

    if newspaper == "times":
        print("starting preprocessing newspaper 'The Times'.")
        df = pd.read_json('times_articles.json')
        print("transformed JSON to dataframe.")
        # content = df.loc[:, "content"]

    elif newspaper == "sun":
        print("starting preprocessing newspaper 'The Sun'.")
        df = pd.read_json('sun_articles.json')
        print("transformed JSON to dataframe.")
        # content = df.loc[:, "content"]

    elif newspaper == "guardian":
        print("starting preprocessing newspaper 'The Guardian'.")
        # for the guardian
        # Create an empty list to store the contents of each JSON file
        json_data = []
        # Set the path to the directory containing the JSON files
        path_to_json_files = "crawler/guardian_articles"
        # Loop through each file in the directory
        for filename in os.listdir(path_to_json_files):
            if filename.endswith(".json"):
                # Open the file and load its contents as a JSON object
                with open(os.path.join(path_to_json_files, filename)) as f:
                    data = json.load(f)
                    # Append the contents to the list
                    json_data.append(data["response"]["results"])

        new_dict_list = []
        for item in json_data:
            for article in item:
                new_dict = {
                    "title": article["webTitle"],
                    "date": article["webPublicationDate"],
                    "content": article["fields"]["body"]
                }
                new_dict_list.append(new_dict)
        # convert the list of dictionaries to a JSON string
        # json_string = json.dumps(new_dict_list)

        # print the JSON string
        # print(json_string)
        df = pd.DataFrame(new_dict_list)
        print("transformed JSON to dataframe.")

    else:
        raise ValueError('Input newspaper is not processable')

    playerlist = fetch_playerlist()

    # preprocessing starts here
    df['sentences'] = df['content'].apply(lambda x: nltk.sent_tokenize(x))
    print("tokenised into sentences.")
    # Tokenize each document into words and remove punctuation
    df['tokens'] = df['content'].apply(lambda x: [word.lower() for word in word_tokenize(x) if word not in punctuation])
    print("tokenised into words.")
    print(f"number of tokens: {len(df['tokens'].explode())}")
    # Remove stopwords
    stopwords_list = stopwords.words('english')
    df['tokens'] = df['tokens'].apply(lambda x: [word for word in x if word not in stopwords_list])
    print("removed stopwords.")
    print(f"number of tokens: {len(df['tokens'].explode())}")
    # Remove symbols
    df['tokens'] = df['tokens'].apply(lambda x: [word for word in x if word.isalpha()])
    print("removed symbols.")
    print(f"number of tokens: {len(df['tokens'].explode())}")
    df['pos_tags'] = df['tokens'].apply(lambda x: nltk.pos_tag(x))
    print("assigned pos tags.")
    # Lemmatise each token
    lemmatiser = WordNetLemmatizer()
    df['lemmas'] = df['tokens'].apply(lambda x: [lemmatiser.lemmatize(token) for token in x])
    print("lemmatised tokens.")
    print(f"number of tokens: {len(df['lemmas'].explode())}")
    df['lemmas'] = df['lemmas'].apply(lambda x: [token for token in x if token not in playerlist])
    print("removed playerlist tokens.")
    print(f"number of tokens: {len(df['lemmas'].explode())}")
    # Convert the list of lemmas back to text
    df['lemmatised_text'] = df['lemmas'].apply(lambda x: ' '.join(x))
    print("rejoined text with lemmas.")

    # Get a list of all tokens
    all_tokens = [token for doc in df['lemmas'] for token in doc]
    # Create a Counter object to count the frequency of each token
    token_counts = Counter(all_tokens)
    # Get a list of tokens that appear less than 10 times
    rare_tokens = [token for token, count in token_counts.items() if count < 10]
    print(f"number of tokens appearing less than ten times: {len(rare_tokens)}")
    # Filter out rare tokens
    print(f"number of tokens: {len(df['lemmas'].explode())}")
    df['lemmas'] = [[token for token in doc if token not in rare_tokens] for doc in df['lemmas']]
    print("removed rare tokens.")
    # Remove rows where there are no tokens left
    df = df[df['lemmas'].map(len) > 0]
    print(f"number of tokens: {len(df['lemmas'].explode())}")

    if csv == True:
        df.to_csv(f'{newspaper}.csv', index=False)

        return print(f"Created file '{newspaper}.csv'.")
    else:
        return df


# dataframe = preprocess("times")
# print(dataframe)
