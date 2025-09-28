from pymilvus import MilvusClient
from sentence_transformers import SentenceTransformer

client = MilvusClient("documents.db")

if client.has_collection(collection_name="documents"):
    client.drop_collection(collection_name="documents")
client.create_collection(
    collection_name="documents",
    dimension=312,  # The vectors we will use in this demo has 768 dimensions
)


from pymilvus import model
# If connection to https://huggingface.co/ failed, uncomment the following path
#import os
#os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'


model = SentenceTransformer('cointegrated/rubert-tiny2')
#model = SentenceTransformer('ai-forever/sbert_large_mt_nlu_ru')

'''
sentences = ["привет мир", "hello world", "здравствуй вселенная"]
embeddings = model.encode(sentences)
print(embeddings)
'''

# This will download a small embedding model "paraphrase-albert-small-v2" (~50MB).
embedding_fn = model.encode
