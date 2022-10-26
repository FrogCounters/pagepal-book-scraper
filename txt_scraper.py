from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import re
import os
source = r'https://www.gutenberg.org/ebooks/23625.txt.utf-8'
TEXT_FOLDER = r"texts"

# soup = BeautifulSoup(urlopen(source),'html.parser')
def _txt_clean(text): #cleans nicely encoded text from get_txt
    no_start = re.split("\*{3}.*PROJECT GUTENBERG EBOOK.*\*{3}", text)[1] #regex for matching ***START OF THE PROJECT GUTENBERG  ...*** this works for cats and kittens
    clean_text = re.split("\*{3}.*PROJECT GUTENBERG EBOOK.*\*{3}", no_start)[0]
    return clean_text.replace("\r\n","\n")



def get_save_sentences(source, title):
    request = requests.get(source)
    request.encoding = request.apparent_encoding
    request.text

    filename_raw = title + "_raw.txt"
    filename = title + ".txt"

    with open(os.path.join(r"scraped_texts", filename_raw), "w", encoding=request.apparent_encoding) as f:
        clean = _txt_clean(request.text)
        print(clean, file=f)

    with open(os.path.join(TEXT_FOLDER, filename), "w", encoding=request.apparent_encoding) as f:
        lines = clean.split("\n")
        # first_new_line = True
        # second_new_line = True
        
        for line in lines:
            if None == re.search("\[.*Illustration.*\]", line):
                if line:
                    f.write(line + " ")
                    first_new_line = True
                    second_new_line = True
                else:
                    # if first_new_line:
                    #     f.write("\n")
                    #     first_new_line = False
                    # elif second_new_line:
                    #     f.write("\n")
                    #     second_new_line = False
                    f.write("\n")
    
    paragraphs = []
    with open(os.path.join(TEXT_FOLDER, filename), "r", encoding=request.apparent_encoding) as f:
        for line in f:
            paragraphs.append(line)
    
    return paragraphs

if __name__ == "__main__":
    get_save_sentences(source, "The Test Book")