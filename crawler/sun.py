import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import os
import io


class SunSpider(scrapy.Spider):
    name = "sun"
    # using only one query to start with
    start_urls = ["https://www.thesun.co.uk/?s=qatar+world+cup"]
    # all result pages ( = including Sep 2022; range 2 to 128 bc page one is differently named ^)
    for i in range(2, 128):
        start_urls.append(f"https://www.thesun.co.uk/page/{i}/?s=qatar+world+cup%2F")

    try:
        os.remove("sun_hrefList.txt")
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
        article_links = sel.css("a.teaser-anchor--search::attr(href)").getall()

        for link in article_links:
            with io.open("sun_hrefList.txt", "a", encoding="utf8") as file:
                file.write(link + "\n")
            yield scrapy.Request(link, callback=self.parse_article)

    def parse_article(self, response):
        """parses an article for metadata and yields a dictionary containing them as key value pairs."""
        title = response.css("h1.article__headline::text").get()
        author = response.css("a.article__author-link::text").get()
        date = response.css("span.article__timestamp::text").get()

        content = " ".join(response.css("div.article__content p::text").getall())

        yield {
            "title": title,
            #"author": author,
            "date": date,
            "content": content,
        }

    def closed(self, reason):
        """closes webdriver"""
        self.driver.quit()
