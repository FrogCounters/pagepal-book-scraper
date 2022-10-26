import codecs
from bs4 import BeautifulSoup
import requests
import re
import os
import json
from urllib.request import urlopen
from api_requests import Analyzer

from txt_scraper import get_save_sentences

TARGET = r"raw_analysis/"
ANALYSIS = r"refined_analysis/"
EAI = Analyzer()

def get_urls(urls = None): #gets lits of urls to access
    if not urls:
        # urls = [r"https://www.gutenberg.org/files/18155/18155-h/18155-h.htm"]
        # urls = [
            # r"https://www.gutenberg.org/files/18155/18155-h/18155-h.htm",
            # r"https://www.gutenberg.org/files/61852/61852-h/61852-h.htm",
            # r"https://www.gutenberg.org/files/32662/32662-h/32662-h.htm",
            # r"https://www.gutenberg.org/cache/epub/23625/pg23625-images.html"]
        
        # using_home_urls
        urls = [
            r"https://www.gutenberg.org/ebooks/23625", # magi pudding
            r"https://www.gutenberg.org/ebooks/61852", # kittens and cats
            # r"https://www.gutenberg.org/ebooks/18155", # three little pigs
            r"https://www.gutenberg.org/ebooks/32662", #  eight stories for isabel
            r"https://www.gutenberg.org/ebooks/21914", #the woggle bug book
            r"https://www.gutenberg.org/ebooks/57844", #the adventure of jimmy brown
            r"https://www.gutenberg.org/ebooks/29595", #funny little socks
            r"https://www.gutenberg.org/ebooks/54995", #uncle wiggily's fortune
            r"https://www.gutenberg.org/ebooks/20097", #the tail of Mrs. ladybug
            r"https://www.gutenberg.org/ebooks/15281", #uncle wiggily's adventure
            r"https://www.gutenberg.org/ebooks/25529", #the adventure's of Danny Meadow Mouse
        ]
    return urls

def _txt_clean(text): #cleans nicely encoded text from get_txt
    no_start = re.split("\*{3}START OF THE PROJECT GUTENBERG EBOOK.*\*{3}", text)[1] #regex for matching ***START OF THE PROJECT GUTENBERG  ...*** this works for cats and kittens
    clean_text = re.split("\*{3}END OF THE PROJECT GUTENBERG EBOOK.*\*{3}", no_start)[0]
    return clean_text

def get_single_txt(source):
    r = requests.get(source)
    r.encoding = r.apparent_encoding
    edited_text = _txt_clean(r.text)

    title = ""
    author = ""

    return (title, author, edited_text, source)

def save_txt(data, target = "texts/"):
    title = data[0]
    author = data[1]
    txt = data[2]
    url = data[3]
    if not os.path.isdir(target):
        os.mkdir(target)

    title = "Cats and Kittens"
    filename = title + ".txt"

    filepath = os.path.join(target, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(txt)
    
    return

def get_single_html(source):
    source = urlopen(source).url
    soup = BeautifulSoup(urlopen(source), "html.parser")
    corpus = []
    title = ""
    author = ""
    img = ""
    hate_speech = []

    flag_ = False
    start_found = True
    end_found = True
    title_found = False
    author_found = False
    res = ""
    # Find All Paragraph that belongs to the story and add it to `corpus`
    for tag in soup.findAll('p'):
        # Finds Start of Story
        if "START OF THE PROJECT GUTENBERG EBOOK"in tag.text or "START OF THE PROJECT GUTENBERG EBOOK"in tag.text:
            flag_ = True
            continue
        # Finds End of Story
        if "END OF THE PROJECT GUTENBERG EBOOK"in tag.text or "START OF THE PROJECT GUTENBERG EBOOK" in tag.text:
            flag_ = False
            break
        # Skip Blank Row Paragraphs
        if flag_:
            if tag.text.replace("/r/n", "").strip() and not tag.text == "<br/>":
                res = tag.text
                if res.strip():
                    corpus.append(res)
                res = ""
        if not title_found:
            if "title:" in tag.text.lower():
                title = tag.text.lstrip("Title:").strip()
                title_found = True
        if not author_found:
            if "author:" in tag.text.lower():
                author = tag.text.lstrip("Author:").strip()
                author_found = True
    
    # Find First Image
    for tag in soup.findAll('img'):
        if not img:
            try:
                img = os.path.dirname(source) + "/" + str(tag.attrs['src'])

            except Exception as e:
                raise e

    
    return [title, author, corpus, source, img, hate_speech]

def save_html(data, target = "texts/"):
    title = data[0]
    author = data[1]
    corpus = data[2]
    url = data[3]
    img = data[4]
    hate_speech = data[5]

    if not os.path.isdir(target):
        os.mkdir(target)
    
    _save(title, url, corpus, [], hate_speech, author, img)

    return

def find_html_url(soup):
    base = "https://www.gutenberg.org"
    links = soup.find_all("a")

    for link in links:
        if "HTML5" in link.text:
            href = link.get("href")
            return base + href

def find_txt_url(soup):
    base = "https://www.gutenberg.org"
    links = soup.find_all("a")

    for link in links:
        if "Plain Text" in link.text:
            href = link.get("href")
            return base + href

def get_direct(home_url):
    print("Finding HTML and TXT links for", home_url)
    soup = BeautifulSoup(urlopen(home_url), "html.parser")
    html_url = find_html_url(soup)
    txt_url = find_txt_url(soup)
    print("Parsing HTML file")
    html_data = get_single_html(html_url) #[title, author, corpus, source, img, hate_speech]
    print("Parsing Txt file")
    paragraphs = get_save_sentences(txt_url, html_data[0])
    html_data[2] = paragraphs
    print("Analysing ebook", html_data[0])
    save_html(html_data)
    print("Saved ebook", html_data[0])
    return
    #find txt url


def _save(title, url, text, emotions, hate_speech, author, main_img = ""):

    txtpath = os.path.join(TARGET, title + ".txt")
    jsonpath = os.path.join(ANALYSIS, title + ".json")
    clean_paras = text

    with open(txtpath, "w", encoding = "utf-8") as f:
        for line in clean_paras:
            f.write(line)

    if os.path.exists(jsonpath):
        return

    sentences = EAI.split_para(clean_paras)
    emotions = EAI.emotions_from_list(sentences)
    hate_speech = list(map(EAI.hate_from_string, sentences))

    result_dic = {
        "title": title,
        "url": url,
        "text": sentences,
        "emotions": emotions,
        "hate_speech": hate_speech,
        "author": author,
        "main_img": main_img
    }

    with open(jsonpath, "w") as f:
        json.dump(result_dic, f, indent=2)



def main():
    urls = get_urls()
    # for url in urls:
    #     if url.endswith(".txt"):
    #         save_txt(get_single_txt(url))
    #     if url.endswith(".htm") or url.endswith(".html"):
    #         save_html(get_single_html(url))
    for url in urls:
        print(get_direct(url))


if __name__ == "__main__":
    main()