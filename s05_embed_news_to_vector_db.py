from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np

# Connect to MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['news_database']
collection = db['news']

# Connect to Qdrant
qdrant_client = QdrantClient("localhost", port=6333)

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create a new collection in Qdrant
collection_name = "news_vectors"
if not qdrant_client.collection_exists(collection_name): 
    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )

# Function to create embedding
def create_embedding(title, subtitle):
    text = f"{title} {subtitle}"
    return model.encode(text)

# Fetch articles from MongoDB
articles = list(collection.find({"title": {"$exists": True}, "subtitle": {"$exists": True}}))

# Process articles and upload to Qdrant
batch_size = 100
for i in tqdm(range(0, len(articles), batch_size), desc="Processing articles"):
    batch = articles[i:i+batch_size]
    
    ids = []
    vectors = []
    payloads = []
    
    for article in batch:
        embedding = create_embedding(article['title'], article['subtitle'])
        
        ids.append(str(article['_id']))
        vectors.append(embedding.tolist())
        payloads.append({
            'title': article['title'],
            'subtitle': article['subtitle'],
            'url': article['url'],
            'date': article['date'].isoformat(),
            'domain': article['domain']
        })
    
    # Upload batch to Qdrant
    qdrant_client.upsert(
        collection_name=collection_name,
        points=zip(ids, vectors, payloads)
    )

print(f"Uploaded {len(articles)} articles to Qdrant")

# Optionally, you can perform a test search
test_query = "banking regulations"
test_vector = model.encode(test_query).tolist()

search_result = qdrant_client.search(
    collection_name=collection_name,
    query_vector=test_vector,
    limit=5
)

print("\nTest search results:")
for result in search_result:
    print(f"Score: {result.score:.4f}, Title: {result.payload['title']}")