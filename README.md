# Qatar World Cup UK Newspaper Analysis

## Newspapers

### Tabloids

- The Sun

### Broadsheet

- The Guardian
- The Times

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


