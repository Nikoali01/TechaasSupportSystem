import time
from pymongo import MongoClient
from bson import ObjectId

# Initialize MongoDB connection
uri = "mongodb://localhost:27017"
client = MongoClient(uri)
db = client['requests']
collection = db['requestsCollection']


def get_next_ticket_id():
    max_ticket = collection.find_one(sort=[("ticket_id", -1)])
    if max_ticket and "ticket_id" in max_ticket:
        next_ticket_id = int(max_ticket["ticket_id"]) + 1
    else:
        next_ticket_id = 1
    return str(next_ticket_id)


def create_ticket(ticket_id, user_id):
    ticket = {
        "ticket_id": ticket_id,
        "user_id": user_id,
        "is_answered": True,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "closed_at": None,
        "status": "Opened",
        "user_rating": None,
        "messages": []
    }
    collection.insert_one(ticket)
    return ticket


def find_ticket(ticket_id):
    return collection.find_one({"ticket_id": ticket_id})


def update_ticket(ticket_id, update_fields):
    collection.update_one({"ticket_id": ticket_id}, {"$set": update_fields})


def add_ticket_message(ticket_id, message):
    collection.update_one({"ticket_id": ticket_id}, {"$push": {"messages": message}})


def change_ticket_answered(ticket_id, is_answered):
    collection.update_one({"ticket_id": ticket_id}, {"$set": {"is_answered": is_answered}})