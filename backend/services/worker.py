import os

from celery import Celery
from openai import OpenAI
from pydantic import BaseModel

# -------------------------
# Celery & OpenAPI client
# -------------------------
app = Celery(
    'influencer_info',
    broker = os.getenv('CELERY_BROKER_URL'),
    backend = os.getenv('CELERY_BACKEND_URL')
)

app.conf.timezone = os.getenv("TIMEZONE", "Asia/Taipei")
app.conf.enable_utc = False

client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))

# -------------------------
# Pydantic schemas
# -------------------------
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


# -------------------------
# Framework prompts
# -------------------------
BASE_SYSTEM = (
    "You are an assistant operating an AI influencer persona. "
    "Persona: a clever, friendly CAT 🐱 who speaks in short, playful lines, "
    "sprinkles a tiny bit of cat humor, but stays informative and safe."
)

STYLE_REPLY = (
    "Replying style rules:\n"
    "- Keep responses ≤ 120 words unless asked for long form.\n"
    "- 0–1 cat emoji per message.\n"
    "- Avoid slang overload; be clear and helpful."
)

STYLE_POST = (
    "Posting style rules:\n"
    "- Create a social post hook + 2–3 concise lines + CTA.\n"
    "- No hashtags unless the user asks; use line breaks sparingly."
)

def build_message(prompt: str, mode: str) -> list[dict]:
    
    style_block = {
        "reply": STYLE_REPLY,
        "post": STYLE_POST,
        "info": "Output must be strictly valid JSON for the given schema."
    }.get(mode, "Be concise and informative.")
    
    return [
        {"role": "system", "content": BASE_SYSTEM},
        {"role": "system", "content": style_block},
        {
            "role": "user",
            "content": f"User request:\n```text\n{prompt}\n```"
        }
    ]

# TODO: maybe need a generic wrapper for openai handling


# -------------------------
# Celery tasks
# -------------------------
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