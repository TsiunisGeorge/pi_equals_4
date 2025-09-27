from pymilvus import MilvusClient

client = MilvusClient("documents.db")

if client.has_collection(collection_name="documents"):
    client.drop_collection(collection_name="documents")
client.create_collection(
    collection_name="documents",
    dimension=312,  # The vectors we will use in this demo has 768 dimensions
)






