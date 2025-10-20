import os, time, random

from celery import Celery, chord, group
from openai import OpenAI
from pydantic import BaseModel

app = Celery(
    'influencer_info',
    broker = os.getenv('CELERY_BROKER_URL'),
    backend = os.getenv('CELERY_BACKEND_URL')
)

client = OpenAI()

# return data
class AvatarInfoA(BaseModel):
    name: str
    age: str
    
class AvatarInfoB(BaseModel):
    habit: list[str]
    fav_food: list[str]

class AvatarReply(BaseModel):
    reply: str
    pass

@app.task
def avatar_info_a(prompt):
    pass


@app.task
def avatar_info_b(prompt):
    pass

@app.task
def avatar_reply():
    pass