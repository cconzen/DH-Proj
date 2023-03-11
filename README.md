# Qatar World Cup UK Newspaper Analysis

## Newspapers

Newspaper | The Sun | Daily Mail | The Guardian | The Times
--- | --- | --- | --- | ---
type | tabloid | tabloid | broadsheet | broadsheet
timespan | Sep 22 - Feb 23 | Sep 22 - Feb 23 | Sep 22 - Feb 23 | Sep 22 - Feb 23
articles collected | 1270 | 597 | 2199 | 805
mean article length | 433 tokens | 566 tokens | 1304 tokens | 927 tokens 
vocabulary | 17499 lemmas | 24781 lemmas | 39283 lemmas | 22586 lemmas
complete articles | yes | yes | yes | yes
tokens complete | 549898 | 1461468 |  2608640 | 746153
without stopwords | 307902 | 852484 |  1473926 | 412010
without symbols | 271541 | 754718 |  1273947 | 362093
lemmas final | 225749 | 667615 |  1138170 | 301143

## Crawlers

Crawlers are written to scrape articles from September 2022 including February 2023.

### The Sun, Daily Mail

Selenium to preload pages + Scrapy to crawl and scrape

### The Times

Selenium to preload and login; Scrapy and Selenium to crawl and scrape

start crawler in terminal with 

````
scrapy runspider [crawler.py] -o [articles .json or .csv]
````

### The Guardian

Guardian API + BeautifulSoup4 to clean body html

run script in .py file

## Functions

most functions can be found in preprocessing.py and methods.py

### preprocessing.py
#### def preprocess(newspaper, csv=False, rare=False)

Preprocesses text data from JSON files for four different newspapers (The Times, The Sun, Daily Mail and The Guardian), including tokenisation, removal of stopwords, punctuation, rare tokens and player names, part-of-speech tagging, and lemmatisation. Depending on <b>csv</b> It returns a Pandas DataFrame containing the preprocessed data or writes a csv file; <b>rare</b> toggles whether rare tokens (= tokens appearing less than ten times) are kept in or not.
````
dataframe = preprocess("sun",csv=False,rare=True)

preprocess("guardian",csv=True)

preprocess("times",csv=True,rare=True)
````
### methods.py
#### def df_to_dtm(df)
Converts a pandas DataFrame of preprocessed text data (obtained using preprocessing() ) into a Document-Term Matrix (DTM) using a CountVectorizer.
````
dtm_dataframe = df_to_dtm(dataframe)
````
#### def df_to_tfidf(df)
Converts a pandas DataFrame of preprocessed text data (obtained using preprocessing() ) into a Term Frequency-Inverse Document Frequency (TF-IDF) matrix using a CountVectorizer and a TfidfTransformer.
````
df_tfidf = df_to_tfidf(dataframe)
````
#### def csv_to_tfidf(file_path)
Converts a CSV file of preprocessed text data (obtained using preprocessing() ) into a Term Frequency-Inverse Document Frequency (TF-IDF) matrix using a CountVectorizer and a TfidfTransformer.
````
df_tfidf_guardian = csv_to_tfidf("guardian.csv")
````
#### def get_term_position(df_tfidf, term)
Gets the column index of a given term in a TF-IDF matrix represented by a pandas DataFrame.
````
get_term_position(df_tfidf_guardian, "climate")
````
#### def compare_term_position(term)
Compares the positions of a given term in the TF-IDF matrices of four different CSV files and write the results to a new CSV file.
````
compare_term_position("climate")
````
#### def read_csv_files()
Reads the CSV files for The Guardian, Daily Mail, The Times, and The Sun and returns them as dataframes.

#### def plot_tfidf(term, save=False)
Plots the development of the normalised TF-IDF score for a given term across four UK newspapers: The Times, Daily Mail, The Sun, and The Guardian, for the period between September 2022 and February 2023.
````
plot_tfidf("lgbt", save=True)
````
#### def get_vocab_from_csv(csv_file, lemma_col='lemmas')
Reads a CSV file containing lemmas and returns a set of unique lemmas (the vocabulary).
````
times_vocab = get_vocab_from_csv("times_rare.csv")
````
#### def get_avg_token_length(vocab)
Calculates the average length of tokens in a vocabulary (input vocabulary must be a set).
````
get_avg_token_length(times_vocab)
````

## Analysis

vocabulary comparison

Topic modelling

cooccurrence measures

in rStudio

## Visualisation

time series

grouping of sentiments 

heatmaps 





