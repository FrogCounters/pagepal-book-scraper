from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import re
import os
import env
source = r'https://www.gutenberg.org/ebooks/23625.txt.utf-8'
DOWNLOAD_TXT_FOLDER = env.PLAIN_TXT_DIR
TEXT_FOLDER = env.CLEANED_TXT_DIR

def _txt_clean(text): #cleans nicely encoded text from get_txt
    no_start = re.split("\*{3}.*START OF T[a-zA-Z]+ PROJECT GUTENBERG.*\n{0,3}.+\*{2}", text)[1] #regex for matching ***START OF THE PROJECT GUTENBERG  ...*** this works for cats and kittens
    clean_text = re.split("\*{3}.*END OF T[a-zA-Z]+ PROJECT GUTENBERG.*\n{0,3}.+\*{2}", no_start)[0]
    return clean_text.replace("\r\n","\n")



def get_save_sentences(source, title):
    request = requests.get(source)
    request.encoding = request.apparent_encoding
    request.text

    filename_raw = title + "_raw.txt"
    filename = title + ".txt"

    with open(os.path.join(DOWNLOAD_TXT_FOLDER, filename_raw), "w", encoding=request.apparent_encoding) as f:
        print(request.text, file=f)

    clean = _txt_clean(request.text)
    lines = clean.split("\n")
    with open(os.path.join(TEXT_FOLDER, filename), "w", encoding=request.apparent_encoding) as f:
        for line in lines:
            line = re.sub("\[.*Illustration.*\]", "\n", line)
            if line:
                f.write(line + " ")
            else:
                f.write("\n")
    
    paragraphs = []
    with open(os.path.join(TEXT_FOLDER, filename), "r", encoding=request.apparent_encoding) as f:
        for line in f:
            paragraphs.append(line)
    
    return paragraphs

if __name__ == "__main__":
    get_save_sentences(source, "The Test Book")