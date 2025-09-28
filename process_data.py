import re
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import WordPunctTokenizer

from frst import client
from hardcode_value import db, save_db, load_db
from frst import embedding_fn

nltk.download('punkt')
nltk.download('stopwords')
replace_list = '@#!?+&amp;*[]-%.:/();$=&gt;&lt;|{}^,.:!?»«' + "'`" + '_'
stemmer = SnowballStemmer("russian")
tokenizer = WordPunctTokenizer()
sw = stopwords.words("russian")


# def get_clean_parts(text):
#     chapters = re.split(r'\n(?=\d+\.\s)', text)
#     return [chapter.strip() for chapter in chapters if chapter.strip()]


def get_clean_parts(text):
    chapters1 = re.split(r'\n(?=\d+\.)', text)
    chapters2 = re.split(r'\n(?=\d+\.\s)', text)

    return chapters1 + [chapter.strip() for chapter in chapters2 if chapter.strip()] + [text[i:i+512] for i in range(0, len(text), 512)]

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


def process(text, name: str):
    data = []
    chunks = get_clean_parts(text)
    for i, chunk in enumerate(chunks):
        data.append(
            {
                "id": i,
                "vector": embedding_fn(
                    preprocess_text(chunk)
                ),
                "text": chunk,
                "metadata": {},  # add any metadata here
            }
        )
        db[i] = chunk + ' источник:' + name
    save_db(db, 'save_db.json')
    client.insert(collection_name="documents", data=data)


def search(query):
    query_vector = embedding_fn(preprocess_text(query))
    res = client.search(
        collection_name="documents",
        anns_field="vector",
        data=[query_vector],
        limit=10,
        search_params={
            "params": {
                "radius": 0.60,
                "range_filter": 1
            }
        }
    )
    list_res = []
    for hits in res:
        for hit in hits:
            list_res.append(db[hit["id"]])

    return remove_substrings(list_res)

def remove_substrings(lines: list[str]) -> list[str]:
    seen = set()
    unique_lines = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    result = []
    for i, line in enumerate(unique_lines):
        is_substring = any(line in other and line != other for j, other in enumerate(unique_lines) if i != j)
        if not is_substring:
            result.append(line)

    return result

def add_to_db(filename):

    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()
    process(text, filename)

# print(text)

#add_to_db("LPA_text_code.txt")



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

#add_to_db("LPA_text_code.txt")
save_db(db, 'save_db.json')
