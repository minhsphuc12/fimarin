# Install MongoDB
brew tap mongodb/brew
brew install mongodb-community@6.0
brew services start mongodb/brew/mongodb-community@6.0
brew --prefix mongodb-community

# Add MongoDB to the PATH
export PATH="/opt/homebrew/opt/mongodb-community@6.0/bin:$PATH"

# Start the MongoDB server
mongod

# Install the MongoDB Shell
brew install mongosh

# MongoDB configuration file
/opt/homebrew/etc/mongod.conf 

# Start MongoDB Server
mongod

# Connect to MongoDB, use mongosh instead of mongo
mongosh 

# Stop MongoDB Server
mongod --shutdown

# Restore a MongoDB Database
mongorestore

# Dump a MongoDB Database
mongodump

# MongoDB Status
mongostat

# MongoDB Top
mongotop

# List all databases
show dbs

# Access a database
use news

# List all collections in the current database
show collections

# Access a collection
db.articles

# Manual Insert an Entry
db.test.insertOne({ "name": "John Doe", "age": 30, "email": "john.doe@example.com" })

# Check the Latest Inserted Record to a Collection
db.news.find().sort({ "_id": -1 }).limit(1)

# Drop a Collection
db.news.drop()

# Check if a URL exists in a collection
db.news.find({ url: "https://example.com" })

# Insert or update a record
db.news.updateOne({ url: "https://example.com" }, { $set: { title: "New Title" } }, { upsert: true })

# Insert or update multiple records
db.news.insertMany([
    { url: "https://example.com", title: "Example 1" },
    { url: "https://example.com/2", title: "Example 2" }
])

# Delete a record
db.news.deleteOne({ url: "https://example.com" })

# Remove all category fields from all records
db.articles.updateMany({}, { $unset: { category: "" } })