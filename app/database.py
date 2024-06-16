import time
from pymongo import MongoClient
from bson import ObjectId

uri = "mongodb://localhost:27017"
client = MongoClient(uri)
db = client['requests']
collection = db['requestsCollection']


def get_next_ticket_id():
    max_ticket = collection.aggregate([
        {"$addFields": {"ticket_id_int": {"$toInt": "$ticket_id"}}},
        {"$sort": {"ticket_id_int": -1}},
        {"$limit": 1}
    ])
    max_ticket = list(max_ticket)  # Convert the cursor to a list
    if max_ticket:
        next_ticket_id = int(max_ticket[0]["ticket_id"]) + 1
    else:
        next_ticket_id = 1
    return str(next_ticket_id)


def create_ticket(ticket_id, user_id):
    ticket = {
        "ticket_id": ticket_id,
        "user_id": user_id,
        "is_answered": False,
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


def find_tickets_by_user_id(user_id):
    tickets_cursor = collection.find({"user_id": user_id}, {"ticket_id": 1, "_id": 0})
    ticket_ids = [ticket["ticket_id"] for ticket in tickets_cursor]
    return ticket_ids


def get_messages_from_ticket(ticket_id):
    ticket = collection.find_one({"ticket_id": ticket_id})
    messages = ticket["messages"]
    response = []
    for message in messages:
        if message["from_"] == "ai":
            response.append({"system": message["content"]})
        else:
            response.append({"user": message["content"]})
    return response
