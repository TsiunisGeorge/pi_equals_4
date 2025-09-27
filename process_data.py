from frst import client
import re
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pymystem3 import Mystem
from nltk.tokenize import WordPunctTokenizer
from nltk.stem import SnowballStemmer
from scnd import embedding_fn
from hardcode_value import LPA_text_1, db
import tqdm


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
    #replace_list = '\n:,\'".:!?1234567890№()»«-'


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
                "vector": embedding_fn(preprocess_text(chunk)),  # your embedding function
                "text": chunk,
                "metadata": {},  # add any metadata here
            }
        )
        db[i] = chunk
    client.insert(collection_name="documents", data=data)

filename = "LPA_text_code.txt"

with open(filename, "r", encoding="utf-8") as file:
    text = file.read()

#print(text)

process(text)




# 4. Single vector search
print("ok1")
query_vector = embedding_fn(preprocess_text("Задачи Совета Министров Республики Беларусь по интеграции государственных информационных ресурсов с общегосударственной автоматизированной информационной системой и по механизму подтверждения уплаты за административные процедуры"))
print("ok2")
res = client.search(
    collection_name="documents",
    anns_field="vector",
    data=[query_vector],
    limit=20,
    search_params={
        "params": {
            "radius": 0.7,
            "range_filter": 1
        }}
)
print("ok3")
for hits in res:
    for hit in hits:
        print(hit)
        print(db[hit["id"]])



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