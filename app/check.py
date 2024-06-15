from pymongo import MongoClient
from datetime import datetime

# MongoDB connection URI
uri = "mongodb://localhost:27017"

# Connect to MongoDB
client = MongoClient(uri)
db = client['requests']
collection = db['requestsCollection']

# Sample JSON documents
tickets = [
    {
        "ticket_id": "1",
        "user_id": "123456789",
        "started_at": "2024-06-14T10:00:00Z",
        "closed_at": "2024-06-14T10:00:10Z",
        "status": "Closed",
        "user_rating": 4,
        "messages": [
            {
                "message_id": "1",
                "from": "user",
                "to": "ai",
                "timestamp": "2024-06-14T10:00:00Z",
                "content": "Привет! Меня зовут Иван, я из компании Oriflame"
            },
            {
                "message_id": "2",
                "from": "ai",
                "to": "user",
                "timestamp": "2024-06-14T10:00:05Z",
                "content": "Я ИИ!"
            }
        ]
    },
    {
        "ticket_id": "2",
        "user_id": "987654321",
        "started_at": "2024-06-15T10:00:00Z",
        "status": "Opened",
        "closed_at": None,
        "user_rating": None,
        "messages": [
            {
                "message_id": "3",
                "from": "user",
                "to": "ai",
                "timestamp": "2024-06-14T10:00:00Z",
                "content": "Привет! Меня зовут Владимир, я из компании Oriflame"
            }
        ]
    }
]

# Function to convert ISO 8601 string to datetime


# Convert date strings to datetime objects
tickets = [convert_to_datetime(ticket) for ticket in tickets]

# Insert the JSON documents into the collection
result = collection.insert_many(tickets)
print(f"Inserted document IDs: {result.inserted_ids}")

# Close the MongoDB connection
client.close()
