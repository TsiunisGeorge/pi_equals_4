import re
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import WordPunctTokenizer

from AI_asistant import generate_question
from frst import client
from hardcode_value import db, save_db, load_db
from scnd import embedding_fn

nltk.download('punkt')
nltk.download('stopwords')
replace_list = '@#!?+&amp;*[]-%.:/();$=&gt;&lt;|{}^0123456789,.:!?»«' + "'`" + '_'
stemmer = SnowballStemmer("russian")
tokenizer = WordPunctTokenizer()
sw = stopwords.words("russian")


# def get_clean_parts(text):
#     chapters = re.split(r'\n(?=\d+\.\s)', text)
#     return [chapter.strip() for chapter in chapters if chapter.strip()]


def get_clean_parts(text):
    chapters1 = re.split(r'\n(?=\d+\.)', text)
    chapters2 = re.split(r'\n(?=\d+\.\s)', text)
    return chapters1 + [chapter.strip() for chapter in chapters2 if chapter.strip()]

def preprocess(text):
    chapters = get_clean_parts(text)
    # replace_list = '\n:,\'".:!?1234567890№()»«-'


def preprocess_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    text = text.lower()
    text = ' '.join([word.lower() for word in text.split() if word.lower() not in sw])

    for r in replace_list:
        text = text.replace(r, '')

    tokens = tokenizer.tokenize(text)
    stemmed_words = [stemmer.stem(word) for word in tokens]
    return ' '.join(stemmed_words)


def process(text):
    data = []
    chunks = get_clean_parts(text)
    for i, chunk in enumerate(chunks):
        data.append(
            {
                "id": i,
                "vector": embedding_fn(
                    preprocess_text(
                        generate_question(chunk)
                    )
                ),
                "text": chunk,
                "metadata": {},  # add any metadata here
            }
        )
        db[i] = chunk
    client.insert(collection_name="documents", data=data)


def search(query):
    query_vector = embedding_fn(preprocess_text(query))
    res = client.search(
        collection_name="documents",
        anns_field="vector",
        data=[query_vector],
        limit=50,
        search_params={
            "params": {
                "radius": 0.7,
                "range_filter": 1
            }
        }
    )
    list_res = []
    for hits in res:
        for hit in hits:
            list_res.append(db[hit["id"]])

    return list_res

def add_to_db(filename):

    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()
    process(text)

# print(text)


'''

res = client.search(
    collection_name="quick_setup",
    anns_field="text",
    data=["ПОСТАНОВЛЯЮ"],
    limit=3,
    search_params={"metric_type": "IP"}
)

for hits in res:
    for hit in hits:
        print(hit)

'''



save_db(db, 'save_db.json')
