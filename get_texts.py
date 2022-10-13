import requests
import re
import os

def get_urls(urls = None): #gets lits of urls to access
    if not urls:
        urls = ["https://www.gutenberg.org/files/61852/61852-0.txt"]

    return urls

def clean(text): #cleans nicely encoded text from get_txt
    clean_text = re.split("\*{3}[a-zA-Z ]*\*{3}", text) #regex for matching ***START OF THE PROJECT GUTENBERG  ...*** this works for cats and kittens
    return clean_text[1]

def get_txt(sources): #gets texts using various methods
    res = []

    for s in sources:
        r = requests.get(s)
        r.encoding = r.apparent_encoding
        edited_text = clean(r.text)

        res.append(edited_text)
    
    return res

def save_txt(txt, target = "texts/"): #saves all texts
    if not os.path.isdir(target):
        os.mkdir(target)
    # title = str(len([f for f in os.listdir(target)])) + ".txt"
    title = "Cats and Kittens" + ".txt"

    filepath = os.path.join(target, title)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(txt)
    
    return

def main():
    urls = get_urls()
    for t in get_txt(urls):
        save_txt(t)

if __name__ == "__main__":
    main()