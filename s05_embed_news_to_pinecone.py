import os
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["news"]
collection = db["articles"]

# Pinecone setup
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Create index if it doesn't exist
if INDEX_NAME not in pc.list_indexes():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,  # Dimension for 'all-MiniLM-L6-v2' model
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-west-2"
        )
    )

# Initialize the index
index = pc.Index(INDEX_NAME)

# Initialize the embedding model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def embed_and_upsert(batch):
    texts = [f"{item['title']} {item['subtitle']}" for item in batch]
    embeddings = model.encode(texts)
    
    vectors = []
    for i, item in enumerate(batch):
        vector = {
            "id": str(item["_id"]),
            "values": embeddings[i].tolist(),
            "metadata": {
                "title": item["title"],
                "subtitle": item["subtitle"],
                "url": item["url"],
                "category": item["category"],
                "published_date": str(item["published_date"])
            }
        }
        vectors.append(vector)
    
    index.upsert(vectors=vectors)

def process_articles():
    batch_size = 100
    batch = []
    
    for article in collection.find():
        batch.append(article)
        if len(batch) == batch_size:
            embed_and_upsert(batch)
            batch = []
    
    if batch:
        embed_and_upsert(batch)

if __name__ == "__main__":
    process_articles()
    print("Finished embedding and uploading articles to Pinecone.")