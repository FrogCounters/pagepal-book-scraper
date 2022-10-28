import os
import json
from textwrap import indent
import env

dir = env.ANALYSED_JSON_DIR

for file in os.listdir(dir):
    filepath = os.path.join(dir, file)
    with open(filepath, "r", encoding="utf8") as f:
        book = json.load(f)
    new_sentences = []
    old_sentences = book["text"]
    emotions = book["emotions"]
    old_hatespeech = book["hate_speech"]
    new_emotions = []
    new_hatespeech = []

    if len(emotions) != len(old_sentences):
        raise Exception
    reduce = False
    for i in range(len(emotions)):
        if not reduce or old_sentences[i] != "\n":
            new_sentences.append(old_sentences[i])
            new_emotions.append(emotions[i])
            new_hatespeech.append(old_hatespeech[i])
            reduce = False
        if old_sentences[i] == "\n":
            reduce = True
    
    book["text"] = new_sentences
    book["emotions"] = new_emotions
    book["hate_speech"] = new_hatespeech

    with open(filepath, "w", encoding="utf8") as j:
        json.dump(book, j, indent=2)
