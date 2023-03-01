# Qatar World Cup UK Newspaper Analysis

## Newspapers

Newspaper | The Sun | The Guardian | The Times
--- | --- | --- | --- 
type | tabloid | broadsheet | broadsheet
timespan | a year | a year | a year 
articles collected | 2200 | 2883 | 999
mean article length | 133 tokens | 1476 tokens | 448 tokens 
vocabulary | 22403 lemmas | 49337 lemmas | 9866 lemmas
complete articles | yes | yes | no
tokens complete | 994494 | 4253975 | 133208
without stopwords | 556366 | 2420775 | 74849
without symbols | 488244 | 2098132 | 67148
lemmas final | 425417 | 1924954 | 45447
## Crawlers

all crawlers track back one year only

### The Sun & The Times

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





