from pydantic import BaseModel
from typing import List
from typing import Dict

class Question(BaseModel):
    message_id: str
    ticket_id: str
    question: str


class Items(BaseModel):
    messages: List[Dict[str, str]]


class Answer(BaseModel):
    message_id: str
    answer: str
