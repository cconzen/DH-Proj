# Qatar World Cup UK Newspaper Analysis

## Newspapers

Newspaper | The Sun | The Guardian | The Times
--- | --- | --- | --- 
type | tabloid | broadsheet | broadsheet
articles collected | 2200 | 2883 | 999

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





