import nltk
import wordnet
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from string import punctuation

lemmatizer = WordNetLemmatizer()
df = pd.read_json('sun_articles.json')


# selecting column with articles
content = df.loc[:, "content"]

df['sentences'] = df['content'].apply(lambda x: nltk.sent_tokenize(x))
# Tokenize each document into words and remove punctuation
df['tokens'] = df['content'].apply(lambda x: [word.lower() for word in word_tokenize(x) if word not in punctuation])
# Remove stopwords
stopwords_list = stopwords.words('english')
df['tokens'] = df['tokens'].apply(lambda x: [word for word in x if word not in stopwords_list])
# Remove symbols
df['tokens'] = df['tokens'].apply(lambda x: [word for word in x if word.isalpha()])


df['pos_tags'] = df['tokens'].apply(lambda x: nltk.pos_tag(x))
# Lemmatize each token
df['lemmas'] = df['tokens'].apply(lambda x: [lemmatizer.lemmatize(token) for token in x])
# Convert the list of lemmas back to text
df['lemmatized_text'] = df['lemmas'].apply(lambda x: ' '.join(x))

# Create a CountVectorizer object
vectorizer = CountVectorizer()
dtm = vectorizer.fit_transform(df['lemmatized_text'])
# Create a dataframe from the DTM
df_dtm = pd.DataFrame(dtm.toarray(), columns=vectorizer.get_feature_names_out())

# Add the original text column back to the dataframe
df_dtm['content'] = df['content']

# Print the resulting dataframe
print(df_dtm)
print(df)



