from vector_store import create_collection, retrieve_from_db
from embedding import model

collection = create_collection()

query = "中国的首都是哪里？"

query_embedding = model.encode(query)

results = retrieve_from_db(
    collection,
    query_embedding,
    top_k=3,
    distance_threshold=1.0
)

print(results)