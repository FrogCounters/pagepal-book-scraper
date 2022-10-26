from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests

source = r"https://www.gutenberg.org/cache/epub/23625/pg23625-images.html"

soup = BeautifulSoup(urlopen(source),'html.parser')
start_found = False
with open("html_scrape_raw.txt", "w") as f:
    print(soup.prettify(),file=f)

book = ""
for part in soup.find_all(["span","p"]):
    if part.name == "span":
        if "*** START OF THIS PROJECT GUTENBERG EBOOK ***" in part.text:
            start_found = True
    
    if start_found:
        if part.name == "p":
            # print(part.find("a"))
            book += part.text.replace("\r\n", "\n") + "\n"

with open("html_scrape_truncated.txt", "w") as f:
    print(book,file=f)