from pymilvus import model
from sentence_transformers import SentenceTransformer
# If connection to https://huggingface.co/ failed, uncomment the following path
#import os
#os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'


#model = SentenceTransformer('cointegrated/rubert-tiny2')
model = SentenceTransformer('ai-forever/sbert_large_mt_nlu_ru')

'''
sentences = ["привет мир", "hello world", "здравствуй вселенная"]
embeddings = model.encode(sentences)
print(embeddings)
'''

# This will download a small embedding model "paraphrase-albert-small-v2" (~50MB).
embedding_fn = model.encode

# Text strings to search from.
docs = [
    "Artificial intelligence was founded as an academic discipline in 1956.",
    "Alan Turing was the first person to conduct substantial research in AI.",
    "Born in Maida Vale, London, Turing was raised in southern England.",
]

vectors = embedding_fn(docs)
# The output vector has 768 dimensions, matching the collection that we just created.
print(vectors[0].shape)  # Dim: 768 (768,)

# Each entity has id, vector representation, raw text, and a subject label that we use
# to demo metadata filtering later.
data = [
    {"id": i, "vector": vectors[i], "text": docs[i], "subject": "history"}
    for i in range(len(vectors))
]

print("Data has", len(data), "entities, each with fields: ", data[0].keys())
print("Vector dim:", len(data[0]["vector"]))

