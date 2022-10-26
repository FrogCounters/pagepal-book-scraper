from urllib.request import urlopen
from bs4 import BeautifulSoup
import os

source = r"https://www.gutenberg.org/ebooks/23625"
base = r"https://www.gutenberg.org"

soup = BeautifulSoup(urlopen(source), "html.parser")

links = soup.find_all("a")

for link in links:
    if "HTML5" in link.text:
        # print(source)
        href = link.get("href")
        res = base + href
        print (res)