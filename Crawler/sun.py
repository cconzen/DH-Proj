import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector


class SunSpider(scrapy.Spider):
    name = "sun"

    # using only one query to start with
    start_urls = ["https://www.thesun.co.uk/?s=qatar+world+cup"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # comment line to make browser visible
        self.driver = webdriver.Chrome(options=chrome_options)

    def parse(self, response, **kwargs):
        self.driver.get(response.url)
        sel = Selector(text=self.driver.page_source)
        article_links = sel.css("a.teaser-anchor--search::attr(href)").getall()
        for link in article_links:
            with open("sun_hreflist.txt", 'a') as file:
                file.truncate()
                file.write(link + "\n")
            yield scrapy.Request(link, callback=self.parse_article)

    def parse_article(self, response):
        title = response.css("h1.article__headline::text").get()
        author = response.css("a.article__author-link::text").get()
        date = response.css("span.article__timestamp::text").get()

        content = " ".join(response.css("div.article__content p::text").getall())

        yield {
            "title": title,
            "author": author,
            "date": date,
            "content": content,
        }

    def closed(self, reason):
        self.driver.quit()
