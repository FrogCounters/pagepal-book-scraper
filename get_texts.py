from bs4 import BeautifulSoup
import requests
import re
import os
import json
import env
from urllib.request import urlopen
from api_requests import Analyzer

from txt_scraper import get_save_sentences

TARGET = env.CLEANED_TXT_DIR #where to take truncated unprocessed texts from
ANALYSIS = env.PRE_PROCESSED_JSONS_DIR #where to save preprocessed jsons
ANALYSIS_TXT = env.PRE_PROCESSED_TXT_DIR #where to save preprocessed texts
ANALYSED_DIR = env.ANALYSED_JSON_DIR

EAI = Analyzer()

def get_urls(urls = None): #gets lits of urls to access
    if not urls:
        urls = [
            r"https://www.gutenberg.org/ebooks/23625", #magic pudding
            r"https://www.gutenberg.org/ebooks/61852", #kittens and cats
            r"https://www.gutenberg.org/ebooks/18155", #three little pigs
            r"https://www.gutenberg.org/ebooks/32662", #eight stories for isabel # change photo
            r"https://www.gutenberg.org/ebooks/21914", #the woggle bug book
            r"https://www.gutenberg.org/ebooks/57844", #the adventure of jimmy brown
            r"https://www.gutenberg.org/ebooks/29595", #funny little socks
            r"https://www.gutenberg.org/ebooks/54995", #uncle wiggily's fortune
            r"https://www.gutenberg.org/ebooks/20097", #the tail of Mrs. ladybug
            r"https://www.gutenberg.org/ebooks/15281", #uncle wiggily's adventure
            r"https://www.gutenberg.org/ebooks/25529", #the adventure's of Danny Meadow Mouse
        ]
    return urls

def get_single_html(source):
    source = urlopen(source).url
    soup = BeautifulSoup(urlopen(source), "html.parser")
    corpus = []
    title = ""
    author = ""
    img = ""
    hate_speech = []

    title_found = False
    author_found = False
    # Find All Paragraph that belongs to the story and add it to `corpus`
    for tag in soup.findAll('p'):
        if title_found and author_found:
            break
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
                break

            except Exception as e:
                raise e

    
    return [title, author, corpus, source, img, hate_speech]

def save_html(data):
    title = data[0]
    author = data[1]
    corpus = data[2]
    url = data[3]
    img = data[4]
    hate_speech = data[5]

    _save(title, url, corpus, [], hate_speech, author, img)

    return

def reduce_newlines(sentences):
    res = []
    reduce = False
    for sentence in sentences:
        if not reduce or sentence != "\n":
            res.append(sentence)
            reduce = False
        if sentence == "\n":
            reduce = True

def _save(title, url, text, emotions, hate_speech, author, main_img = ""):

    txtpath = os.path.join(ANALYSIS_TXT, title + ".txt")
    jsonpath = os.path.join(ANALYSIS, title + ".json")
    final_jsonpath = os.path.join(ANALYSED_DIR, title + ".json")
    clean_paras = text

    if os.path.exists(final_jsonpath):
        print(final_jsonpath, "already exists, skipping...")
        return

    sentences = EAI.split_para(clean_paras)
    sentences = reduce_newlines(sentences)

    with open(txtpath, "w", encoding = "utf-8") as f:
        for sentence in sentences:
            f.write(sentence)

    emotions = [] #moved to analyse_jsons
    hate_speech = [] #moved to analyse_jsons
    
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

def get_direct(home_url):
    
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

    print("Finding HTML and TXT links for", home_url)
    soup = BeautifulSoup(urlopen(home_url), "html.parser")
    html_url = find_html_url(soup)
    txt_url = find_txt_url(soup)
    print("Parsing HTML file")
    html_data = get_single_html(html_url) 
    print("Parsing Txt file")
    paragraphs = get_save_sentences(txt_url, html_data[0])
    html_data[2] = paragraphs
    print("Analysing ebook", html_data[0])
    save_html(html_data)
    print("Saved ebook", html_data[0])
    return
    #find txt url

def main():
    urls = get_urls()
    for url in urls:
        print(get_direct(url))


if __name__ == "__main__":
    main()