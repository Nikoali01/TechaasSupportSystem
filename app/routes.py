from fastapi import APIRouter, HTTPException
from app.database import collection, get_next_ticket_id, create_ticket
from bson import ObjectId
from app.models import Ticket, StartTicketRequest, CloseTicketRequest

router = APIRouter()


@router.post("/start_ticket")
async def return_ticket(request: StartTicketRequest):
    new_id = get_next_ticket_id()
    create_ticket(new_id, request.user_id)
    return {"ticket_id": new_id}


@router.get("/ticket/{ticket_id}")
async def get_ticket(ticket_id: str):
    ticket = collection.find_one({"ticket_id": ticket_id})
    print(ticket)
    if ticket:
        return Ticket(**ticket)
    else:
        raise HTTPException(status_code=404, detail="Ticket not found")


@router.patch("/ticket/{ticket_id}/close")
async def close_ticket(ticket_id: str, request: CloseTicketRequest):
    ticket = collection.find_one({"ticket_id": ticket_id})
    print(ticket)
    if ticket:
        collection.update_one(
            {"_id": ObjectId(ticket["_id"])},
            {"$set": {"status": "Closed", "user_rating": request.user_rating}}
        )
        return {"message": "Ticket closed successfully"}
    else:
        raise HTTPException(status_code=404, detail="Ticket not found")


@router.post("/ticket/{ticket_id}/add_message")
async def add_message(ticket_id: str, message: dict):
    ticket = collection.find_one({"ticket_id": ticket_id})
    if ticket:
        collection.update_one({"_id": ObjectId(ticket["_id"])}, {"$push": {"messages": message}})
        return {"message": "Message added successfully"}
    else:
        raise HTTPException(status_code=404, detail="Ticket not found")