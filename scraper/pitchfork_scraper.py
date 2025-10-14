from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
import time

class PitchforkScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def scroll_down(self, times):
        body = self.driver.find_element("tag name", "body")
        for _ in range(times):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.5)

    def get_artist_links(self, url):
        self.driver.get(url)
        self.scroll_down(1)
        html = self.driver.execute_script("return document.documentElement.outerHTML")
        soup = BeautifulSoup(html, 'lxml')
        self.driver.quit()

        artist_dict = {}
        ul = soup.find("ul", {"class": "artist-full-list"})
        if not ul: return artist_dict

        for li in ul.find_all("li"):
            name_tag = li.find("span", {"class": "artist-image__name"})
            link_tag = li.find("a", {"class": "artist-image"})
            if name_tag and link_tag and 'href' in link_tag.attrs:
                artist_dict[name_tag.text] = "https://pitchfork.com" + link_tag['href']
        return artist_dict

    def get_artist_albums(self, artist_url):
        page = requests.get(artist_url).text
        soup = BeautifulSoup(page, 'lxml')
        albums = []

        ul = soup.find("ul", {"class": "results-fragment"})
        if not ul: return albums

        for li in ul.find_all("li"):
            title = li.find("h2", {"class": "review__title-album"})
            date = li.find("time", {"class": "pub-date"})
            if title and date:
                albums.append((title.text, date['datetime']))
        return albums
