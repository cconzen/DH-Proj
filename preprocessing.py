import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from string import punctuation
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import pandas as pd
import os
import json


def preprocess(newspaper="sun"):
    """
        Preprocesses text data from JSON files for three different newspapers (The Times, The Sun, and The Guardian),
        including tokenisation, removal of stopwords and punctuation, part-of-speech tagging, and lemmatisation.
        Returns a Pandas DataFrame containing the preprocessed data.

        Parameters:
        -----------
        newspaper : str, default="sun"
            Name of the newspaper to preprocess data for. Must be one of "times", "sun", or "guardian".

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
        df = pd.read_json('times_articles.json')
        # content = df.loc[:, "content"]

    elif newspaper == "sun":
        df = pd.read_json('sun_articles.json')
        # content = df.loc[:, "content"]

    elif newspaper == "guardian":
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

    else:
        raise ValueError('Input newspaper is not processable')

    # preprocessing starts here
    df['sentences'] = df['content'].apply(lambda x: nltk.sent_tokenize(x))
    # Tokenize each document into words and remove punctuation
    df['tokens'] = df['content'].apply(lambda x: [word.lower() for word in word_tokenize(x) if word not in punctuation])
    # Remove stopwords
    stopwords_list = stopwords.words('english')
    df['tokens'] = df['tokens'].apply(lambda x: [word for word in x if word not in stopwords_list])
    # Remove symbols
    df['tokens'] = df['tokens'].apply(lambda x: [word for word in x if word.isalpha()])

    df['pos_tags'] = df['tokens'].apply(lambda x: nltk.pos_tag(x))
    # Lemmatise each token
    lemmatiser = WordNetLemmatizer()
    df['lemmas'] = df['tokens'].apply(lambda x: [lemmatiser.lemmatize(token) for token in x])
    # Convert the list of lemmas back to text
    df['lemmatised_text'] = df['lemmas'].apply(lambda x: ' '.join(x))

    return df


def df_to_dtm(df):
    """
       Convert a pandas DataFrame of preprocessed text data (obtained using preprocessing() ) into a Document-Term Matrix
       (DTM) using a CountVectorizer.

       Parameters:
           df (pandas DataFrame): A DataFrame containing preprocessed text data, including a column named 'lemmatised_text'
                                  containing the preprocessed text data as strings.

       Returns:
           pandas DataFrame: A DataFrame representation of the DTM with document IDs as the index and individual terms as
                             columns. The cells of the DataFrame contain the term frequencies (counts) for each document.
    """

    # Create a CountVectorizer object
    vectoriser = CountVectorizer()
    dtm = vectoriser.fit_transform(df['lemmatised_text'])
    # Create a dataframe from the DTM
    df_dtm = pd.DataFrame(dtm.toarray(), columns=vectoriser.get_feature_names_out())
    # Add the original text column back to the dataframe
    df_dtm['content'] = df['content']

    return df_dtm


def df_to_tfidf(df):
    """
        Convert a pandas DataFrame of preprocessed text data (obtained using preprocessing() ) into a Term Frequency-Inverse
        Document Frequency (TF-IDF) matrix using a CountVectorizer and a TfidfTransformer.

        Parameters:
            df (pandas DataFrame): A DataFrame containing preprocessed text data, including a column named 'lemmatised_text'
                                   containing the preprocessed text data as strings.

        Returns:
            pandas DataFrame: A DataFrame representation of the TF-IDF matrix with document IDs as the index and individual
                              terms as columns. The cells of the DataFrame contain the TF-IDF scores for each document.
    """

    vectoriser = CountVectorizer()
    dtm = vectoriser.fit_transform(df['lemmatised_text'])
    tfidf_transformer = TfidfTransformer()
    tfidf = tfidf_transformer.fit_transform(dtm)
    # Create a dataframe from the TF-IDF matrix
    df_tfidf = pd.DataFrame(tfidf.toarray(), columns=vectoriser.get_feature_names_out())
    df_tfidf = df_tfidf[df_tfidf.sum().sort_values(ascending=False).index]
    # Add the original text column back to the dataframe
    df_tfidf['content'] = df['content']
    pd.set_option('display.max_columns', 100)
    # Print the resulting dataframe

    return df_tfidf

#dataframe = preprocess("guardian")
#dtm_dataframe = df_to_dtm(dataframe)
#print(df_to_tfidf(dataframe))
