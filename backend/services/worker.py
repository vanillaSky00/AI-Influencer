import os

from celery import Celery
from openai import OpenAI
from pydantic import BaseModel

app = Celery(
    'influencer_info',
    broker = os.getenv('CELERY_BROKER_URL'),
    backend = os.getenv('CELERY_BACKEND_URL')
)

client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

class AvatarInfoA(BaseModel):
    name: str
    age: str
    
class AvatarInfoB(BaseModel):
    habit: list[str]
    fav_food: list[str]

class AvatarReply(BaseModel):
    reply: str
    
class AvatarPost(BaseModel):
    post: str

def build_reply_message(prompt) -> list[dict]:
    return [
        {"role": "system", "content": BASE_SYSTEM},
        {"role": "system", "content": STYLE_GUIDE},
        {
            "role": "user",
            "content": f"User request:\n```text\n{prompt}\n```"
        }
    ]

def build_post_message(prompt) -> list[dict]:
    return [
        {"role": "system", "content": BASE_SYSTEM},
        {"role": "system", "content": STYLE_GUIDE},
        {
            "role": "user",
            "content": f"User request:\n```text\n{prompt}\n```"
        }        
    ]

@app.task
def avatar_info_a(prompt):
    
    response = client.beta.chat.completions.parse(
        model = 'gpt-4o-mini',
        messages = build_message(prompt),
        response_format = AvatarInfoA,
    )
    
    avatar_a = AvatarInfoA.model_validate_json(response.choices[0].message.content)
    
    return avatar_a.model_dump()

@app.task
def avatar_info_b(prompt):
    response = client.beta.chat.completions.parse(
        model = 'gpt-4o-mini',
        messages = build_message(prompt),
        response_format = AvatarInfoB,
    )
    
    avatar_b = AvatarInfoB.model_validate_json(response)
    
    return avatar_b.model_dump();

@app.task
def avatar_reply(prompt):
    response = client.beta.chat.completions.parse(
        model = 'gpt-4o-mini',
        messages = build_message(prompt),
        response_format = AvatarReply,
    )
    
    avatar_r = AvatarReply.model_validate_json(response);
    
    return avatar_r.model_dump() 

@app.task
def avatar_post(prompt):
    response = client.beta.chat.completions.parse(
        model = 'gpt-4o-mini',
        messages = build_message(prompt),
        response_format = AvatarPost,
    )
    
    avatar_p = AvatarPost.model_validate_json(response);
    
    return avatar_p.model_dump() 

@app.task
def combine_parts(parts):
    merged = {}
    
    for part in parts:
        merged.update(part)
        
    return merged