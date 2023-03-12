
# Exercise: Frequency analysis

options(stringsAsFactors = FALSE)
require(quanteda)
library(dplyr)
require(readtext)

#textdata <- read.csv("./data/qatar/sun.csv", encoding = "UTF-8")
#textdata <- read.csv("./data/qatar/mail.csv", encoding = "UTF-8")
textdata <- read.csv("./data/qatar/guardian.csv", encoding = "UTF-8")
#textdata <- read.csv("./data/qatar/times.csv", encoding = "UTF-8")


textdata$date <- as.Date(textdata$date, format = "%Y-%m-%d")

# we add some more metadata columns to the data frame

textdata$month <- substr(textdata$date, 4, 5)
textdata$month <- format(as.Date(textdata$date, "%d.%m.%Y"), "%m")

textdata$month <- as.numeric(format(textdata$date, "%m"))

str(textdata$month)

library(lubridate)

textdata$month <- as.factor(textdata$month)


length(textdata$month)


#sotu_corpus <- corpus(readtext("./data/qatar/sun.csv", text_field = "lemmatised_text"))
#sotu_corpus <- corpus(readtext("./data/qatar/mail.csv", text_field = "lemmatised_text"))
sotu_corpus <- corpus(readtext("./data/qatar/guardian.csv", text_field = "lemmatised_text"))
#sotu_corpus <- corpus(readtext("./data/qatar/times.csv", text_field = "lemmatised_text"))


# Build a dictionary of lemmas
lemma_data <- read.csv("./resources/baseform_en.tsv", encoding = "UTF-8")
# Create a DTM
corpus_tokens <- sotu_corpus %>%
  tokens(remove_punct = TRUE, remove_numbers = TRUE, remove_symbols = TRUE) %>%
  tokens_tolower() %>%
  tokens_replace(lemma_data$inflected_form, lemma_data$lemma,
                 valuetype = "fixed") %>%
  tokens_remove(pattern = stopwords())


print(paste0("1: ", substr(paste(corpus_tokens[1], collapse = " "),
                           0, 400), "..."))

DTM <- corpus_tokens %>%
  dfm()
dim(DTM)

terms_to_observe <- c("alcohol", "armband", "boycott", "bribery", "climate", "controversy","corruption", "discrimination", "gay", "iran", "lesbian", "lgbt", "migrant", "protest", "russia", "sportswashing")


head(terms_to_observe)

DTM_reduced <- as.matrix(DTM[, terms_to_observe])


counts_per_month <- aggregate(DTM_reduced, by = list(month = textdata$month),
                               sum)

# give x and y values beautiful names
months <- counts_per_month$month
frequencies <- counts_per_month[, terms_to_observe]
# plot multiple frequencies
matplot(months, frequencies, type = "l")
# add legend to the plot
l <- length(terms_to_observe)

legend("topleft", legend = terms_to_observe, col = 1:l, text.col = 1:l,
       lty = 1:l, cex = 0.7)


