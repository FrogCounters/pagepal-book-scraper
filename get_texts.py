import codecs
from bs4 import BeautifulSoup
import requests
import re
import os
import json
from urllib.request import urlopen
from api_requests import Analyzer

TARGET = r"texts/"
ANALYSIS = r"raw_analysis/"
EAI = Analyzer()

def get_urls(urls = None): #gets lits of urls to access
    if not urls:
        # urls = [r"https://www.gutenberg.org/files/18155/18155-h/18155-h.htm"]
        urls = [r"https://www.gutenberg.org/files/18155/18155-h/18155-h.htm", r"https://www.gutenberg.org/files/61852/61852-h/61852-h.htm", r"https://www.gutenberg.org/cache/epub/58550/pg58550-images.html"]
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
    
    soup = BeautifulSoup(urlopen(source), features="xml")
    corpus = []
    title = ""
    author = ""
    flag_ = False
    title_found = False
    author_found = False
    res = ""
    # Find All Paragraph that belongs to the story and add it to `corpus`
    for tag in soup.findAll('p'):
        # Finds Start of Story
        if "START OF THE PROJECT GUTENBERG EBOOK"in tag.text:
            flag_ = True
            continue
        # Finds End of Story
        if "END OF THE PROJECT GUTENBERG EBOOK"in tag.text:
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
            if "Title:" in tag.text:
                title = tag.text.lstrip("Title:").strip()
                title_found = True
        if not author_found:
            if "Author:" in tag.text:
                author = tag.text.lstrip("Author:").strip()
                author_found = True

    
    return (title, author, corpus, source)

def save_html(data, target = "texts/"):
    title = data[0]
    author = data[1]
    corpus = data[2]
    url = data[3]

    if not os.path.isdir(target):
        os.mkdir(target)
    
    _save(title, url, corpus, [], author)

    return

def _save(title, url, text, emotions, author, main_img = ""):

    txtpath = os.path.join(TARGET, title + ".txt")
    jsonpath = os.path.join(ANALYSIS, title + ".json")
    clean_paras = []

    with open(txtpath, "w", encoding="utf-8") as f:
        for para in text:
            clean_paras.append(para.replace("\r\n", " "))

            f.write(para.replace("\r\n", " ") + "\n")

    if os.path.exists(jsonpath):
        return

    sentences = EAI.split_para(clean_paras)
    emotions = EAI.emotions_from_list(sentences)


    result_dic = {
        "title": title,
        "url": url,
        "text": sentences,
        "emotions": emotions,
        "author": author,
        "main_img": main_img
    }


    with open(jsonpath, "w") as f:
        json.dump(result_dic, f, indent=2)



def main():
    urls = get_urls()
    for url in urls:
        if url.endswith(".txt"):
            save_txt(get_single_txt(url))
        if url.endswith(".htm") or url.endswith(".html"):
            save_html(get_single_html(url))


if __name__ == "__main__":
    main()