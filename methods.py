import io
import pandas as pd
import numpy as np
from IPython.core.display_functions import display
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
from matplotlib.dates import MonthLocator, DateFormatter

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

    return col_index


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


def read_csv_files():
    """Reads the CSV files for The Guardian, Daily Mail, The Times, and The Sun and returns them as dataframes.

    Returns:
        tuple: A tuple containing two elements:
            1. A list of pandas dataframes, one for each CSV file.
            2. A list of strings, one for each dataframe, representing the color to use when plotting that dataframe's data.
    """

    filenames = ['guardian.csv', 'mail.csv', 'times.csv', 'sun.csv']
    dataframes = [pd.read_csv(filename) for filename in filenames]
    colors = ['blue', 'red', 'green', 'orange']  # Add colors for each dataframe
    return dataframes, colors


def plot_tfidf(term):
    """Plots the development of the normalised TF-IDF score for a given term across the four newspapers.

       Args:
           term (str): The term for which to plot the TF-IDF score.

       Returns:
           bool: True if the plot was created successfully, otherwise False.
       """
    vectorizer = TfidfVectorizer()
    dataframes, colors = read_csv_files()
    # Create an empty dataframe to store the combined data from all dataframes
    df = pd.DataFrame()

    for i, dataframe in enumerate(dataframes):
        # Calculate the TF-IDF for all text in each dataframe
        tfidf = vectorizer.fit_transform(dataframe['lemmatised_text'])
        # Get the index of the term you want to plot
        term_index = vectorizer.vocabulary_[term]
        # Extract the TF-IDF scores for the selected term
        tfidf_term = tfidf[:, term_index].toarray().ravel()
        # Normalize the TF-IDF scores to be between 0 and 1
        scaler = MinMaxScaler()
        tfidf_term = scaler.fit_transform(tfidf_term.reshape(-1, 1)).ravel()
        # Convert the date column to datetime objects
        dataframe['date'] = pd.to_datetime(dataframe['date'], utc=True)
        # Group by month and calculate the mean TF-IDF score for each month
        tfidf_monthly = dataframe.groupby(dataframe['date'].dt.to_period('M'))['lemmatised_text'].agg(
            ['count', lambda x: np.nanmean(tfidf_term[x.index])])
        tfidf_monthly.columns = ['count', 'tfidf']
        # Add a new column to the dataframe with the color for this dataframe
        tfidf_monthly['color'] = colors[i]
        # Append the data to the combined dataframe
        df = df.append(tfidf_monthly)

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    # Set the x-axis to display months
    months = MonthLocator()
    months_fmt = DateFormatter('%b %Y')
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(months_fmt)

    # Loop through the data for each dataframe and plot the data with the corresponding color
    for color, group in df.groupby('color'):
        group.index = group.index.to_timestamp()
        if color == 'green':
            ax.plot(group.index, group['tfidf'], label='The Times', color=color)
        elif color == 'red':
            ax.plot(group.index, group['tfidf'], label='Daily Mail', color=color)
        elif color == 'orange':
            ax.plot(group.index, group['tfidf'], label='The Sun', color=color)
        else:
            ax.plot(group.index, group['tfidf'], label='The Guardian', color=color)

    # Add labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Normalised TF-IDF score')
    ax.set_title('TF-IDF score development Sep 22 - Feb 23 for term "{}"'.format(term))
    ax.legend()
    plt.show()
    plt.pause(0.001)

    return True

plot_tfidf("gay")
