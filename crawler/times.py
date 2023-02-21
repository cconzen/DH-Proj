import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import os
import io


class TimesSpider(scrapy.Spider):
    name = "times"
    # using only one query to start with
    start_urls = ["https://www.thetimes.co.uk/search?filter=past_year&q=qatar%20world%20cup&source=search-page"]
    # all pages filtered to the last year; range 2 to 149 bc page one is differently named ^)
    for i in range(2, 149):
        start_urls.append(f"https://www.thetimes.co.uk/search?filter=past_year&p={i}&q=qatar%20world%20cup&source=search-page")

    try:
        os.remove("times_hreflist.txt")
    except OSError:
        pass

    def __init__(self, **kwargs):
        """initialise selenium webdriver"""
        super().__init__(**kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # comment line to make browser visible
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse(self, response, **kwargs):
        """parses raw response to get all href links, also writes a txt file containing them."""
        self.driver.get(response.url)
        sel = Selector(text=self.driver.page_source)
        article_links = sel.css("ul.SearchResultList>li>div>h2>a::attr(href)").getall()

        for link in article_links:
            with io.open("times_hrefList.txt", "a", encoding="utf8") as file:
                file.write("https://www.thetimes.co.uk" + link + "\n")
            yield scrapy.Request("https://www.thetimes.co.uk" + link, callback=self.parse_article)

    def parse_article(self, response):
        """parses an article for metadata and yields a dictionary containing them as key value pairs."""
        title = response.css("title::text").get()
        author = response.css("meta[name='author']::attr(content)").get()
        date = response.css("time::attr(datetime)").get()
        # PROBLEM: Paywall cuts off article
        content = " ".join(response.css("article.responsive__BodyContainer-sc-15gvuj2-3 p::text").getall())

        yield {
            "title": title,
            "author": author,
            "date": date,
            "content": content,
        }

    def closed(self, reason):
        """closes webdriver"""
        self.driver.quit()
