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

### The Sun, Daily Mail & The Times

Selenium to preload pages + Scrapy to crawl and scrape

start crawler in terminal with 

````
scrapy runspider [crawler.py] -o [articles .json or .csv]
````

### The Guardian

Guardian API + BeautifulSoup4 to clean body html

run script in .py file

## Analysis

vocabulary comparison

Topic modelling

cooccurrence measures

in rStudio

## Visualisation

time series

grouping of sentiments 

heatmaps 





