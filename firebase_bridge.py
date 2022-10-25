import firebase_admin
from datetime import datetime
from firebase_admin import credentials
from firebase_admin import firestore

cred_obj = credentials.Certificate('firebase_token.json')

app = firebase_admin.initialize_app(cred_obj)

db = firestore.client()


def insert_book(title, url, text, emotions, hate_speech, author, main_img = ""):
    data = {
        u'title': title,
        u'url': url,
        u'text': text,
        u'emotions': emotions,
        u'hate_speech': hate_speech,
        #date uploaded
        u'author': author,
        u'main_img': main_img
    }

    db.collection("books").document(title).set(data)

def get_all_books():
    docs = db.collection("books").stream()   # .where(u'', u'==', True)
    return docs

def get_book(title):
    doc_ref = db.collection("books").document(title)

    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    else:
        return {}

if __name__ == '__main__':
    # insert_book("test title123", "ww.come", "hello", "ma")
    print(get_book("Charlotte's Web"))