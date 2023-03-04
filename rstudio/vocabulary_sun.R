#Exercise: Frequency analysis
# 1 Multi-word tokenization

options(stringsAsFactors = FALSE)
library(quanteda)
# read the SOTU corpus data
textdata <- read.csv("./data/qatar/sun.csv", sep = ";", encoding = "UTF-8")
#sotu_corpus <- corpus(textdata$text, docnames = textdata$doc_id)
sotu_corpus <- corpus(readtext("./data/qatar/sun.csv", text_field = "content"))

# Build a dictionary of lemmas
lemma_data <- read.csv("./resources/baseform_en.tsv", encoding = "UTF-8")
# read an extended stop word list
stopwords_extended <- readLines("./resources/stopwords_en.txt",
                                encoding = "UTF-8")
# Preprocessing of the corpus
corpus_tokens <- sotu_corpus %>%
  tokens(remove_punct = TRUE, remove_numbers = TRUE, remove_symbols = TRUE) %>%
  tokens_tolower() %>%
  tokens_replace(lemma_data$inflected_form, lemma_data$lemma,
                 valuetype = "fixed") %>%
  tokens_remove(pattern = stopwords_extended, padding = T)

# calculate multi-word unit candidates
sotu_collocations <- quanteda.textstats::textstat_collocations(corpus_tokens,
                                                               min_count = 25)
# check top collocations
head(sotu_collocations, 25)

# check bottom collocations
tail(sotu_collocations, 25)

# We will treat the top 250 collocations as MWU
sotu_collocations <- sotu_collocations[1:250, ]

# compound collocations
corpus_tokens <- tokens_compound(corpus_tokens, sotu_collocations)
# corpus_tokens[100]


# Create DTM (also remove padding empty term)
DTM <- corpus_tokens %>%
  tokens_remove("") %>%
  dfm()

#------------------------------

# 2 TF-IDF
# Let us compute TF-IDF weights for all terms in the first speech of Barack Obama.
# Compute IDF: log(N / n_i)
number_of_docs <- nrow(DTM)

#Terme pro Do, Summe der einzelnen Terme
term_in_docs <- colSums(DTM > 0)

idf <- log(number_of_docs/term_in_docs)

# Compute TF
first_obama_speech <- which(textdata$sentences == "summer")[1]

tf <- as.vector(DTM[first_obama_speech, ])
# Compute TF-IDF
tf_idf <- tf * idf
names(tf_idf) <- colnames(DTM)

sort(tf_idf, decreasing = T)[1:20]

# 3 Log likelihood

targetDTM <- DTM
termCountsTarget <- as.vector(targetDTM[first_obama_speech, ])
names(termCountsTarget) <- colnames(targetDTM)
# Just keep counts greater than zero
termCountsTarget <- termCountsTarget[termCountsTarget > 0]


lines <- readLines("./resources/eng_wikipedia_2010_30K-sentences.txt",
                   encoding = "UTF-8")
# lines[10]

corpus_compare <- corpus(lines)

corpus_compare_tokens <- corpus_compare %>%
  tokens(remove_punct = TRUE, remove_numbers = TRUE, remove_symbols = TRUE) %>%
  tokens_tolower() %>%
  tokens_replace(lemma_data$inflected_form, lemma_data$lemma,
                 valuetype = "fixed") %>%
  tokens_remove(pattern = stopwords_extended, padding = T)
# Create DTM
  tokens_compound(sotu_collocations) %>%
  tokens_remove("") %>%
  dfm()
termCountsComparison <- colSums(comparisonDTM)


# Loglikelihood for a single term
term <- "health_care"
# Determine variables
a <- termCountsTarget[term]
b <- termCountsComparison[term]
c <- sum(termCountsTarget)
d <- sum(termCountsComparison)
# Compute log likelihood test

Expected1 = c * (a + b)/(c + d)
Expected2 = d * (a + b)/(c + d)
t1 <- a * log((a/Expected1))
t2 <- b * log((b/Expected2))
logLikelihood <- 2 * (t1 + t2)
print(logLikelihood)


# use set operation to get terms only occurring in target
# document
uniqueTerms <- setdiff(names(termCountsTarget), names(termCountsComparison))
# Have a look into a random selection of terms unique in
# the target corpus
sample(uniqueTerms, 20)


# Create vector of zeros to append to comparison counts
zeroCounts <- rep(0, length(uniqueTerms))
names(zeroCounts) <- uniqueTerms
termCountsComparison <- c(termCountsComparison, zeroCounts)
# Get list of terms to compare from intersection of target
# and comparison vocabulary
termsToCompare <- intersect(names(termCountsTarget), names(termCountsComparison))
# Calculate statistics (same as above, but now with
# vectors!)
a <- termCountsTarget[termsToCompare]
b <- termCountsComparison[termsToCompare]
c <- sum(termCountsTarget)
d <- sum(termCountsComparison)
Expected1 = c * (a + b)/(c + d)
Expected2 = d * (a + b)/(c + d)
t1 <- a * log((a/Expected1) + (a == 0))
t2 <- b * log((b/Expected2) + (b == 0))
logLikelihood <- 2 * (t1 + t2)
# Compare relative frequencies to indicate over/underuse
relA <- a/c
relB <- b/d
# underused terms are multiplied by -1
logLikelihood[relA < relB] <- logLikelihood[relA < relB] * -1


# top terms (overuse in targetCorpus compared to
# comparisonCorpus)
sort(logLikelihood, decreasing = TRUE)[1:50]

# bottom terms (underuse in targetCorpus compared to
# comparisonCorpus)
sort(logLikelihood, decreasing = FALSE)[1:25]


llTop100 <- sort(logLikelihood, decreasing = TRUE)[1:100]
frqTop100 <- termCountsTarget[names(llTop100)]
frqLLcomparison <- data.frame(llTop100, frqTop100)
View(frqLLcomparison)
# Number of signficantly overused terms (p < 0.01)
sum(logLikelihood > 6.63)

# 4 Visualization

require(wordcloud2)
# install.packages("wordcloud2")
top50 <- sort(logLikelihood, decreasing = TRUE)[1:50]
top50_df <- data.frame(word = names(top50), count = top50, row.names = NULL)
wordcloud2(top50_df, shuffle = F, size = 0.2)

# 5 Alternative reference corpora

source("./calculateLogLikelihood.R")
presidents <- unique(textdata$sentences)
for (president in presidents) {
  cat("Extracting terms for president", president, "\n")
  selector_logical_idx <- textdata$president == president
  presidentDTM <- targetDTM[selector_logical_idx, ]
  termCountsTarget <- colSums(presidentDTM)
  otherDTM <- targetDTM[!selector_logical_idx, ]
  termCountsComparison <- colSums(otherDTM)
  loglik_terms <- calculateLogLikelihood(termCountsTarget,
                                         termCountsComparison)
  top50 <- sort(loglik_terms, decreasing = TRUE)[1:50]
  fileName <- paste0("wordclouds/", president, ".pdf")
  pdf(fileName, width = 9, height = 7)
  wordcloud::wordcloud(names(top50), top50, max.words = 50,
                       scale = c(3, 0.9), colors = RColorBrewer::brewer.pal(8,
                                                                            "Dark2"), random.order = F)
  dev.off()
}


# 6 Optional exercises

# 1. Create a table (data.frame), which displays the top 25 terms of all speeches by frequency, tf-idf
# and log likelihood in columns.

# 2. Create a wordcloud which compares Obama’s last speech with all his other speeches.


