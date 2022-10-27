import os
import json
import env
from api_requests import Analyzer
import post_jsons_to_firebase

JSON_SOURCE_DIR = env.PRE_PROCESSED_JSONS_DIR
TXT_SOURCE_DIR = env.PRE_PROCESSED_TXT_DIR
FINAL_JSON_DIR = env.ANALYSED_JSON_DIR
FINAL_TXT_DIR = env.ANALYSED_TXT_DIR
EAI = Analyzer()

def main():
    for file in os.listdir(JSON_SOURCE_DIR):
        with open(os.path.join(JSON_SOURCE_DIR, file), "r", encoding="utf8") as j:
            book_dict = json.load(j)

            if os.path.exists(os.path.join(FINAL_JSON_DIR, file)):
                print(file, "already exists in final directory, skipping...")
                continue
            
            with open(os.path.join(TXT_SOURCE_DIR, book_dict["title"] + ".txt"), "r", encoding="utf8") as t:
                sentences = [line for line in t]
                emotions = EAI.emotions_from_list(sentences)
                hate_speech = list(map(EAI.hate_from_string, sentences))
                book_dict["text"] = sentences
                book_dict["emotions"] = emotions
                book_dict["hate_speech"] = hate_speech

        with open(os.path.join(FINAL_TXT_DIR, book_dict["title"] + ".txt"), "w", encoding = "utf8") as final_t:
            for sentence in book_dict["text"]:
                final_t.write(sentence)
        with open(os.path.join(FINAL_JSON_DIR, file), "w") as final_j:
            json.dump(book_dict, final_j, indent=2)

if __name__ == "__main__":
    main()
    post_jsons_to_firebase.main()
    