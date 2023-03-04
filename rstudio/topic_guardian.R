# setwd('Your work directory')
options(stringsAsFactors = FALSE)
library(quanteda)
require(topicmodels)
require(readtext)


textdata <- read.csv("./data/qatar/guardian.csv", sep = ";", encoding = "UTF-8")
# sotu_corpus <- corpus(textdata$text, docnames = textdata$doc_id)
sotu_corpus <- corpus(readtext("./data/qatar/guardian.csv", text_field = "content"))

# Build a dictionary of lemmas
lemma_data <- read.csv("./resources/baseform_en.tsv", encoding = "UTF-8")
# extended stopword list
stopwords_extended <- readLines("./resources/stopwords_en.txt",
                                encoding = "UTF-8")
# Create a DTM (may take a while)
corpus_tokens <- sotu_corpus %>%
  tokens(remove_punct = TRUE, remove_numbers = TRUE, remove_symbols = TRUE) %>%
  tokens_tolower() %>%
  tokens_replace(lemma_data$inflected_form, lemma_data$lemma,
                 valuetype = "fixed") %>%
  tokens_remove(pattern = stopwords_extended, padding = T)
sotu_collocations <- quanteda.textstats::textstat_collocations(corpus_tokens,
                                                               min_count = 25)
sotu_collocations <- sotu_collocations[1:250, ]
corpus_tokens <- tokens_compound(corpus_tokens, sotu_collocations)


# 1 Model calculation

# Create DTM, but remove terms which occur in less than 1%
# of all documents
DTM <- corpus_tokens %>%
  tokens_remove("") %>%
  dfm() %>%
  dfm_trim(min_docfreq = 0.01, max_docfreq = 0.99, docfreq_type = "prop")
# have a look at the number of documents and terms in the
# matrix
dim(DTM)

top10_terms <- c("qatar", "world", "cup", "corruption",
                 "government", "fifa", "migrant", "champion", "saudi", "arabia")
DTM <- DTM[, !(colnames(DTM) %in% top10_terms)]
# due to vocabulary pruning, we have empty rows in our DTM
# LDA does not like this. So we remove those docs from the
# DTM and the metadata
sel_idx <- rowSums(DTM) > 0
DTM <- DTM[sel_idx, ]
textdata <- textdata[sel_idx, ]

#----------------------- Texte verarbeitet, und Matrix gebildet Dokumenten Term Matrix


# load package topicmodels
require(topicmodels)
# number of topics
K <- 20
# compute the LDA model, inference via n iterations of
# Gibbs sampling
topicModel <- LDA(DTM, K, method = "Gibbs", control = list(iter = 500,
                                                           seed = 1, 
                                                           verbose = 25))
# have a look a some of the results (posterior
# distributions)
tmResult <- posterior(topicModel)
# format of the resulting object
attributes(tmResult)

ncol(DTM) # lengthOfVocab

# topics are probability distribtions over the entire
# vocabulary
beta <- tmResult$terms # get beta from results
dim(beta) # K distributions over ncol(DTM) terms

rowSums(beta) # rows in beta sum to 1
nrow(DTM) # size of collection


# for every document we have a probability distribution of
# its contained topics
theta <- tmResult$topics
#Themen und Wktverteilung
dim(theta) # nDocs(DTM) distributions over K topics

rowSums(theta)[1:10] # rows in theta sum to 1

terms(topicModel, 10)

top5termsPerTopic <- terms(topicModel, 5)
topicNames <- apply(top5termsPerTopic, 2, paste, collapse = " ")


# 2 Visualization

# visualize topics as word cloud
topicToViz <- 11 # change for your own topic of interest
# Or select a topic by a term contained in its name
topicToViz <- grep("qatar", topicNames)[1]
# select to 40 most probable terms from the topic by
# sorting the term-topic-probability vector in decreasing
# order
top40terms <- sort(tmResult$terms[topicToViz, ], decreasing = TRUE)[1:40]
words <- names(top40terms)
# extract the probabilites of each of the 40 terms
probabilities <- sort(tmResult$terms[topicToViz, ], decreasing = TRUE)[1:40]

# visualize the terms as wordcloud
require(wordcloud2)
wordcloud2(data.frame(words, probabilities), shuffle = FALSE)

exampleIds <- c(2, 100, 200)
cat(sotu_corpus[exampleIds[1]])
cat(sotu_corpus[exampleIds[2]])
cat(sotu_corpus[exampleIds[3]])

# load libraries for visualization
library("reshape2")
library("ggplot2")
N <- length(exampleIds)


# get topic proportions form example documents
topicProportionExamples <- theta[exampleIds,]
colnames(topicProportionExamples) <- topicNames
vizDataFrame <- melt(cbind(
  data.frame(topicProportionExamples),
  document = factor(1:N)),
  variable.name = "topic", id.vars = "document")

ggplot(data = vizDataFrame,
       aes(topic, value, fill = document), ylab = "proportion") +
  geom_bar(stat="identity") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  coord_flip() +
  facet_wrap(~ document, ncol = N)


# 3 Topic distributions

# see alpha from previous model
attr(topicModel, "alpha")
K = 30

topicModel2 <- LDA(DTM, K, method = "Gibbs", control = list(iter = 500,
                                                            verbose = 25, 
                                                            seed = 1, 
                                                            alpha = 0.2))

tmResult <- posterior(topicModel2)
theta <- tmResult$topics
beta <- tmResult$terms
# Reset Topic names

topicNames <- apply(terms(topicModel2, 5), 2, paste, collapse = " ")

topicProportionExamples <- theta[exampleIds,]
colnames(topicProportionExamples) <- topicNames
vizDataFrame <- melt(cbind(
  data.frame(topicProportionExamples),
  document = factor(1:N)),
  variable.name = "topic", id.vars = "document")


ggplot(data = vizDataFrame,
       aes(topic, value, fill = document), ylab = "proportion") +
  geom_bar(stat="identity") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1)) +
  coord_flip() +
  facet_wrap(~ document, ncol = N)

# je kleiner alpha desto spezifischer die Aufteilung, wie spitz

# 4 Topic ranking

# re-rank top topic terms for topic names
topicNames <- apply(lda::top.topic.words(beta, 5, by.score = T),
                    2, paste, collapse = " ")

# Approach 1
# What are the most probable topics in the entire
# collection? mean probablities over all paragraphs
topicProportions <- colSums(theta)/nrow(DTM)
# assign the topic names we created before
names(topicProportions) <- topicNames
# show summed proportions in decreased order
sort(topicProportions, decreasing = TRUE)

#--------------------------------------------------------


# Approach 2
countsOfPrimaryTopics <- rep(0, K)
names(countsOfPrimaryTopics) <- topicNames
for (i in 1:nrow(DTM)) {
  # select topic distribution for document i
  topicsPerDoc <- theta[i, ]
  # get first element position from ordered list
  primaryTopic <- order(topicsPerDoc, decreasing = TRUE)[1]
  countsOfPrimaryTopics[primaryTopic] <- countsOfPrimaryTopics[primaryTopic] +
    1
}
sort(countsOfPrimaryTopics, decreasing = TRUE)

#über alle Zielen der DTM, Topicrepräsentation für ein best. Dokument, interriert durch alle
# Doks
# geht in Variable und selektiert primären Dok und setzt Zähler 1 nach oben
# Sortierung zeigt das Landwirtschaft eine rolle spilet, ist anders
#---------------------------------------------------------

# 5 Filtering documents

# you can set this manually ...
topicToFilter <- 6
# ... or have it selected by a term in the topic name
topicToFilter <- grep("qatar ", topicNames)[1]
# minimum share of content must be attributed to the selected topic
topicThreshold <- 0.1
selectedDocumentIndexes <- (theta[, topicToFilter] >= topicThreshold)
filteredCorpus <- sotu_corpus %>%
  corpus_subset(subset = selectedDocumentIndexes)
# show length of filtered corpus
filteredCorpus

# 6 Topic proportions over time

# append decade information for aggregation
textdata$decade <- paste0(substr(textdata$date, 0, 3), "0")
# get mean topic proportions per decade
topic_proportion_per_decade <- aggregate(theta,
                                         by = list(decade = textdata$decade), mean)
# set topic names to aggregated columns
colnames(topic_proportion_per_decade)[2:(K+1)] <- topicNames
# reshape data frame
vizDataFrame <- melt(topic_proportion_per_decade, id.vars = "decade")
# plot topic proportions per deacde as bar plot
require(pals)


ggplot(vizDataFrame,
       aes(x=decade, y=value, fill=variable)) +
  geom_bar(stat = "identity") + ylab("proportion") +
  scale_fill_manual(values = paste0(c(alphabet(30),"#00FF00", "#FF0000", "#0000FF", "#999999"),"FF"), name = "decade") +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))

