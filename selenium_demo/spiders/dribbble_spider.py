import scrapy
import os
from time import sleep
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

basedir = os.path.dirname(os.path.realpath('__file__'))

class DribbbleSpider(scrapy.Spider):
    name = "dribbble"
    allowed_domains = ["dribbble.com"]
    start_urls = ['https://dribbble.com/designers']


    def parse(self, response):

        # download the chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads
        # the version of the driver must match the version of chrome installed to work

        # instantiate a chrome options object so you can set the size and headless preference
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920x1080")

        # comment out the following line if you don't want to actually show Chrome instance
        # but you can still see that the crawling is working via output in console

        # chrome_options.add_argument("--headless")


        # comment out the following two lines to setup ProxyMesh service
        # make sure you add the IP of the machine running this script to you ProxyMesh account for IP authentication
        # IP:PORT or HOST:PORT you get this in your account once you pay for a plan

        # PROXY = "us-wa.proxymesh.com:31280"
        # chrome_options.add_argument('--proxy-server=%s' % PROXY)

        chrome_driver_path = os.path.join(basedir, 'chromedriver')
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver_path)

        driver.get('https://dribbble.com/designers')
        scrapy_selector = Selector(text = driver.page_source)

        self.logger.info("*********** before scrolling ************")
        self.logger.info(scrapy_selector.css('.vcard a[data-subject]::text').getall())
        self.logger.info(len(scrapy_selector.css('.vcard a[data-subject]::text').getall()))

        # designer page with an infinite scroll
        last_height = driver.execute_script("return document.body.scrollHeight")
        SCROLL_PAUSE_TIME = 5
        MAX_SCROLL = 10
        i = 0
        while i <= MAX_SCROLL:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            i += 1
            # IMPORTANT!!!
            # you have to get the selector again after each scrolling
            # in order to get the newly loaded contents
            scrapy_selector = Selector(text = driver.page_source)
            self.logger.info("*********** during scrolling ************")
            self.logger.info("Total scrolls executed: {}".format(i))
            self.logger.info("this is the current designer names extracted: {}".format(scrapy_selector.css('.vcard a[data-subject]::text').getall()))
            self.logger.info("Total names extracted: {}".format(len(scrapy_selector.css('.vcard a[data-subject]::text').getall())))

            sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        self.logger.info("*********** scrolling done ************")
        self.logger.info("final designer names extracted: {}".format(scrapy_selector.css('.vcard a[data-subject]::text').getall()))
        self.logger.info("Final total names extracted: {}".format(len(scrapy_selector.css('.vcard a[data-subject]::text').getall())))

        # the following demostrates how to find the search location box
        # enter "New York" and then click the search button
        search_location = driver.find_element_by_css_selector('#location-selectized').send_keys('New York')
        sleep(1)
        search_button = driver.find_element_by_css_selector('input[type="submit"]')
        search_button.click()
        sleep(5)
