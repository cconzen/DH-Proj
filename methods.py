import io

from IPython.core.display_functions import display

#from preprocessing import preprocess

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
import pandas as pd


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
    display(df_tfidf)
    return df_tfidf

def csv_to_tfidf(file_path):
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
    df = pd.read_csv(file_path)
    vectoriser = CountVectorizer()
    dtm = vectoriser.fit_transform(df['lemmatised_text'])
    tfidf_transformer = TfidfTransformer()
    tfidf = tfidf_transformer.fit_transform(dtm)
    # Create a dataframe from the TF-IDF matrix
    df_tfidf = pd.DataFrame(tfidf.toarray(), columns=vectoriser.get_feature_names_out())
    df_tfidf = df_tfidf[df_tfidf.sum().sort_values(ascending=False).index]
    # Add the original text column back to the dataframe
    df_tfidf['content'] = df['content']
    # Limit the size of the dataframe to 100 rows and 100 columns
    #df_tfidf = df_tfidf.iloc[:100, :500]

    return df_tfidf


def get_term_position(df_tfidf, term):
    # Get the column index of the term
    col_index = df_tfidf.columns.get_loc(term)

    return (col_index)


def compare_term_position(term):

    guardian = csv_to_tfidf("guardian.csv").columns.get_loc(term)
    times = csv_to_tfidf("times.csv").columns.get_loc(term)
    sun = csv_to_tfidf("sun.csv").columns.get_loc(term)
    mail = csv_to_tfidf("mail.csv").columns.get_loc(term)

    with io.open(f"{term}compare.csv", "w", encoding="utf8") as file:
        file.write(f"guardian, {guardian}, times, {times}, sun, {sun}, mail, {mail}")

    return print(f"guardian, {guardian}, times, {times}, sun, {sun}, mail, {mail}")

#dataframe = preprocess("sun")
#print(dataframe)
#dtm_dataframe = df_to_dtm(dataframe)
#compare_term_position("qatar")
#csv_to_tfidf("guardian.csv")

