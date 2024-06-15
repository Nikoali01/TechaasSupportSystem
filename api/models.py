from pydantic import BaseModel


class Question(BaseModel):
    message_id: str
    question: str


class Answer(BaseModel):
    message_id: str
    answer: str

