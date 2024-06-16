from fastapi import APIRouter, HTTPException
from models import Items
from queries import add_message
import os
import openai

client = openai.OpenAI(
    base_url=f"{os.getenv("ML_URL",default="localhost")}/v1",
    api_key="sk-no-key-required"
)

router = APIRouter()


@router.post('/ticket/answer')
def fetch_answer(request: Items):
    message = add_message(request.messages)
    completion = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=message
    )
    response = completion.choices[0].message.content
    return {"message": response}
