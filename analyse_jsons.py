import os
import json
from pprint import pprint

from firebase_bridge import insert_book #insert_book(title, url, text, emotions, author, main_img = "")

JSON_DIR = "raw_analysis"
JSON_PATH = "output.json"

def main():

    for file in os.listdir(JSON_DIR):
    
        if file.endswith(".json"):
            title = file.rstrip(".json")
            with open(os.path.join(JSON_DIR, file), "r", encoding="utf-8") as f:
                raw_json = json.load(f)
                insert_book(**raw_json)

    # pprint(sentiment)

if __name__ == "__main__":
    main()