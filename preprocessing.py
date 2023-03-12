import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from string import punctuation
import pandas as pd
from collections import Counter
# function which gets a list of all player names, used to remove them from the corpus
from get_playernames import fetch_playerlist


def preprocess(newspaper: str, csv: bool = False, rare: bool = False):
    """
        Preprocesses text data from JSON files for four different newspapers (The Times, The Sun, Daily Mail and The Guardian),
        including tokenisation, removal of stopwords, punctuation, rare tokens and player names, part-of-speech tagging,
        and lemmatisation.
        Returns a Pandas DataFrame containing the preprocessed data or creates a csv file depending on csv bool.

        Parameters:
        -----------
        newspaper : str
        Name of the newspaper to preprocess data for. Must be one of "times", "sun", "mail" or "guardian".
        csv : bool, optional
        If True, saves the resulting DataFrame to a CSV file. Defaults to False.
        rare : bool, optional
        If True, rare tokens are not removed from the preprocessed text. Defaults to False.

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
    if newspaper not in ["times", "sun", "guardian", "mail", "dailymail"]:
        raise ValueError('newspaper argument must be one of "times", "sun", or "guardian", "mail" or "dailymail".')

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

    elif newspaper == "mail" or newspaper == "dailymail":
        print("starting preprocessing newspaper 'Daily Mail'.")
        df = pd.read_json('mail_articles.json')
        print("transformed JSON to dataframe.")
        # content = df.loc[:, "content"]

    elif newspaper == "guardian":
        print("starting preprocessing newspaper 'The Guardian'.")
        df = pd.read_json('guardian_articles.json')
        print("transformed JSON to dataframe.")
        # content = df.loc[:, "content"]

    else:
        raise ValueError('Input newspaper is not processable')

    playerlist = fetch_playerlist()
    if 'author' in df.columns:
        df = df.drop('author', axis=1)
    # preprocessing starts here
    df['sentences'] = df['content'].apply(lambda x: nltk.sent_tokenize(x))
    print("tokenised into sentences.")
    # Tokenize each document into words and remove punctuation
    df['tokens'] = df['content'].apply(lambda x: [word.lower() for word in word_tokenize(x) if word not in punctuation])
    print("tokenised into words.")

    df['article_length'] = df['tokens'].apply(len)
    # Calculate the mean of the `article_length` column
    mean_article_length = df['article_length'].mean()
    print(f"Mean article length: {mean_article_length}")

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
    # lemmatise each token
    lemmatiser = WordNetLemmatizer()
    df['lemmas'] = df['tokens'].apply(lambda x: [lemmatiser.lemmatize(token) for token in x])
    print("lemmatised tokens.")

    all_tokens = [token for doc in df['lemmas'] for token in doc]
    # Create a set to remove duplicates and get the vocabulary
    print(f"Vocabulary without stopwords and player names: {len(set(all_tokens)-set(playerlist))}")

    print(f"number of tokens: {len(df['lemmas'].explode())}")
    df['lemmas'] = df['lemmas'].apply(lambda x: [token for token in x if token not in playerlist])
    print("removed playerlist tokens.")

    print(f"number of tokens: {len(df['lemmas'].explode())}")
    # Convert the list of lemmas back to text
    df['lemmatised_text'] = df['lemmas'].apply(lambda x: ' '.join(x))
    print("rejoined text with lemmas.")

    if rare:
        print("rare tokens not removed as rare == TRUE")
    else:
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
        if rare == True:
            name = f'{newspaper}_rare.csv'
            df.to_csv(name, index=False)
        else:
            name = f'{newspaper}.csv'
            df.to_csv(name, index=False)

        return print(f"Created file '{name}'.")
    else:
        return df
