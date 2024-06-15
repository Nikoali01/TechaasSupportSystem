from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class Message(BaseModel):
    message_id: str
    from_: str
    to_: str
    timestamp: datetime
    content: str


class Ticket(BaseModel):
    ticket_id: str
    user_id: str
    is_answered: bool
    started_at: datetime
    closed_at: Optional[datetime]
    status: str
    user_rating: Optional[int]
    messages: List[Message]

    class Config:
        orm_mode = True


class StartTicketRequest(BaseModel):
    user_id: str


class CloseTicketRequest(BaseModel):
    user_rating: int
    ticket_id : str


class AddMessageRequest(BaseModel):
    user_id: str
    ticket_id: str
    message: str
