import pymongo

def insert_to_mongodb(data, collection_name):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["news_database"]
    collection = db[collection_name]

    inserted_count = 0
    for item in data:
        # Insert or update based on the URL
        result = collection.update_one({'url': item['url']}, {'$set': item}, upsert=True)
        if result.upserted_id or result.modified_count > 0:
            inserted_count += 1

    print(f"Inserted/updated {inserted_count} news items in MongoDB collection '{collection_name}'")