import os
import io
import time
from datetime import datetime
import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TimesSpider(scrapy.Spider):
    name = "times"
    # using only one query to start with
    start_urls = ["https://www.thetimes.co.uk/search?filter=past_year&q=qatar%20world%20cup&source=search-page"]

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
        self.driver.get("https://account.thetimes.co.uk/login?state=hKFo2SBHUkR1MnAtT245NWJwQU9McFJVX3lZRE4wcUVtRl96RaFupWxvZ2luo3RpZNkgckdZdGNrMlQwdGluQ1JIUmlRbEdlZXZUX0NiaWxwVVOjY2lk2SBEbXNVM0JCbXltb1VYT1JuWG9xcXJxaUJMTEtJNkl2Sg&client=DmsU3BBmymoUXORnXoqqrqiBLLKI6IvJ&protocol=oauth2&prompt=login&scope=openid%20profile%20email&response_type=code&redirect_uri=https%3A%2F%2Flogin.thetimes.co.uk%2Foidc%2Frp%2Fcallback&nustate=eyJyZXR1cm5fdXJsIjoiaHR0cHM6Ly93d3cudGhldGltZXMuY28udWsvIiwic2lnblVwTGluayI6Imh0dHBzOi8vam9pbi50aGV0aW1lcy5jby51ay8ifQ%3D%3D")
        email = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, "1-email")))
        password = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.NAME, "password")))
        login = self.driver.find_element(By.NAME, "submit")

        email.clear()
        email.send_keys("email")
        password.clear()
        password.send_keys("passwort")
        time.sleep(1)
        login.click()

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
        date_str = response.css("div.tc-text__TcText-sc-15igzev-0 time::attr(datetime)").get()
        # check if date is within September 2022 to February 2023
        title = response.css("title::text").get()
        author = response.css("meta[name='author']::attr(content)").get()

        self.driver.get(response.url)
        content = ""
        try:
            # Wait for the page to load completely
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".responsive__Paragraph-sc-1pktst5-0"))
            )
            # Extract the text content of all p elements with the given class
            paragraphs = self.driver.execute_script(
                "return [...document.querySelectorAll('.responsive__Paragraph-sc-1pktst5-0')].map(x => x.textContent)")
            content = " ".join(paragraphs)
        except:
            pass

        if date_str is not None:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            if date.year == 2022 and date.month >= 9 or date.year == 2023 and date.month <= 2:
                yield {
                    "title": title,
                    "author": author,
                    "date": date_str,
                    "content": content,
                }

    def closed(self, reason):
        """closes webdriver"""
        self.driver.quit()
