# Qdrant Installation and Basic Usage

## Installation

1. Install Docker if you haven't already.

2. Pull the Qdrant Docker image:
   ```
   docker pull qdrant/qdrant
   ```

3. Run Qdrant container:
   ```
   docker run -p 6333:6333 -p 6334:6334 \
     -v $(pwd)/qdrant_storage:/qdrant/storage:z \
     qdrant/qdrant
   ```

   This command runs Qdrant on ports 6333 (HTTP) and 6334 (GRPC), and stores data in the `./qdrant_storage` directory.

## Basic Manual Commands

You can interact with Qdrant using curl commands. Here are some basic operations:

1. Create a collection:
   ```
   curl -X PUT 'http://localhost:6333/collections/news_vectors' \
     -H 'Content-Type: application/json' \
     -d '{
       "vectors": {
         "size": 384,
         "distance": "Cosine"
       }
     }'
   ```

2. Get collection info:
   ```
   curl 'http://localhost:6333/collections/news_vectors'
   ```

3. Insert points:
   ```
   curl -X PUT 'http://localhost:6333/collections/news_vectors/points' \
     -H 'Content-Type: application/json' \
     -d '{
       "points": [
         {
           "id": 1,
           "vector": [0.05, 0.61, 0.76, 0.74],
           "payload": {
             "title": "Sample news title",
             "url": "https://example.com/news/1"
           }
         }
       ]
     }'
   ```

4. Search for similar vectors:
   ```
   curl -X POST 'http://localhost:6333/collections/news_vectors/points/search' \
     -H 'Content-Type: application/json' \
     -d '{
       "vector": [0.2, 0.1, 0.9, 0.7],
       "limit": 3
     }'
   ```

5. Delete a collection:
   ```
   curl -X DELETE 'http://localhost:6333/collections/news_vectors'
   ```

For more detailed information and advanced usage, refer to the [Qdrant documentation](https://qdrant.tech/documentation/).