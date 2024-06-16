import time

from fastapi import APIRouter, HTTPException
from app.database import get_next_ticket_id, create_ticket, find_ticket, update_ticket, add_ticket_message, \
    change_ticket_answered, find_tickets_by_user_id, get_messages_from_ticket
from app.models import Ticket, StartTicketRequest, CloseTicketRequest, AddMessageRequest, GetTicketAnswered
from app.processors import getAnswer

auth_tokens = ["1234"]

router = APIRouter()


@router.post("/start_ticket")
async def return_ticket(request: StartTicketRequest):
    if request.access_token not in auth_tokens:
        raise HTTPException(status_code=403, detail="You are not allowed to do this action")
    else:
        new_id = get_next_ticket_id()
        print(new_id)
        create_ticket(new_id, request.user_id)
        return {"ticket_id": new_id}


@router.get("/{user_id}/tickets")
async def return_tickets_by_user(user_id: str):
    list_of_tickets = find_tickets_by_user_id(user_id)
    return {"tickets": list_of_tickets}


@router.get("/ticket/{ticket_id}")
async def get_ticket(ticket_id: str):
    ticket = find_ticket(ticket_id)
    if ticket:
        return Ticket(**ticket)
    else:
        raise HTTPException(status_code=404, detail="Ticket not found")


@router.patch("/ticket/close")
async def close_ticket(request: CloseTicketRequest):
    if request.access_token not in auth_tokens:
        raise HTTPException(status_code=403, detail="You are not allowed to do this action")
    else:
        ticket = find_ticket(request.ticket_id)
        if ticket:
            update_ticket(request.ticket_id, {"status": "Closed", "user_rating": request.user_rating,
                                              "closed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
            return {"message": "Ticket closed successfully"}
        else:
            raise HTTPException(status_code=404, detail="Ticket not found")


@router.post("/ticket/add_message")
async def add_message(request: AddMessageRequest):
    if request.access_token not in auth_tokens:
        raise HTTPException(status_code=403, detail="You are not allowed to do this action")
    else:
        ticket = find_ticket(request.ticket_id)
        if ticket:
            if ticket["status"] != "Closed":
                if ticket["user_id"] != request.user_id:
                    raise HTTPException(status_code=403, detail="User is not allowed to add messages to this ticket")
                try:
                    last_message_id = ticket["messages"][-1]["message_id"]
                except Exception:
                    last_message_id = "0"
                message = {
                    "from_": "user",
                    "to_": "ai",
                    "content": request.message,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "message_id": str(int(last_message_id) + 1)
                }
                add_ticket_message(request.ticket_id, message)
                change_ticket_answered(request.ticket_id, False)
                messages = get_messages_from_ticket(request.ticket_id)
                print(messages)
                answerr = getAnswer.work(messages)
                resp_message = {
                    "from_": "ai",
                    "to_": "user",
                    "content": answerr["message"],
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "message_id": str(int(last_message_id) + 2)
                }
                add_ticket_message(request.ticket_id, resp_message)
                change_ticket_answered(request.ticket_id, True)
                return {"message": "Message added successfully"}
            else:
                raise HTTPException(status_code=403, detail="The ticket is closed")
        else:
            raise HTTPException(status_code=404, detail="Ticket not found")


@router.post("/ticket/get_updates")
async def get_updates(request: GetTicketAnswered):
    if request.access_token not in auth_tokens:
        raise HTTPException(status_code=403, detail="You are not allowed to do this action")
    else:
        ticket = find_ticket(request.ticket_id)
        if ticket:
            if ticket["status"] != "Closed":
                if ticket["user_id"] != request.user_id:
                    raise HTTPException(status_code=403,
                                        detail="User is not allowed to check messages from this ticket")
                else:
                    if not ticket["is_answered"]:
                        raise HTTPException(status_code=204, detail="Answer is not delivered yet")
                    else:
                        return {"answer": ticket["messages"][len(ticket["messages"]) - 1]["content"]}
            else:
                raise HTTPException(status_code=403, detail="The ticket is closed")
        else:
            raise HTTPException(status_code=404, detail="Ticket not found")
