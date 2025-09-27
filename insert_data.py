from frst import client

data = ""
res = client.insert(collection_name="demo_collection", data=data)

print(res)