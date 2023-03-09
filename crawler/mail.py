import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import os
import io


class MailSpider(scrapy.Spider):
    name = "mail"
    # Error 403 handling by declaring user agent
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"

    # using only one query to start with
    start_urls = ["https://www.dailymail.co.uk/home/search.html?offset=0&size=50&sel=site&searchPhrase=Qatar+World+Cup&type=article&type=article&topic=World+Cup&days=last365days"]

    # off-set = pages, 50 = 1 page
    for i in range(50, 2650, 50):
        start_urls.append(f"https://www.dailymail.co.uk/home/search.html?offset={i}&size=50&sel=site&searchPhrase=Qatar+World+Cup&type=article&type=article&topic=World+Cup&days=last365days")

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
        article_links = sel.css("h3.sch-res-title a::attr(href)").getall()
        if os.path.isfile("mail_hrefList.txt"):
            with open("mail_hrefList.txt", "r") as f:
                linklist = f.readlines()
        else:
            linklist = []

        # duplicate article handling
        for link in article_links:
            link_last_part = link.split("/")[-1]
            if any(link_last_part + "\n" == existing_link.split("/")[-1] for existing_link in linklist):
                continue
            else:
                linklist.append("https://www.dailymail.co.uk" + link + "\n")
                yield scrapy.Request("https://www.dailymail.co.uk" + link, callback=self.parse_article)
        with io.open("mail_hrefList.txt", "w", encoding="utf8") as file:
            [file.write(link) for link in linklist]

    def parse_article(self, response):
        """parses an article for metadata and yields a dictionary containing them as key value pairs."""
        title = response.css("div#js-article-text h2::text").get()
        date = response.css("time::attr(datetime)").get()

        content = " ".join(response.css('div p.mol-para-with-font::text').getall())

        yield {
            "title": title,
            "date": date,
            "content": content,
        }

    def closed(self, reason):
        """closes webdriver"""
        self.driver.quit()

