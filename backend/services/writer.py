import os, json, re, datetime, hashlib
from pathlib import Path
from openai import OpenAI
from sqlalchemy.orm import Session
#from db.session import SessionLocal, Base, engine
#from db.models import Post
#from .memory import add_post_to_memory

BASE_DIR = Path(__file__).resolve().parent          # .../backend/services
DEFAULT_PROMPTS_DIR = BASE_DIR.parent / "prompts"   # .../backend/prompts
PROMPTS_DIR = Path(os.getenv("PROMPTS_DIR", str(DEFAULT_PROMPTS_DIR)))          

#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _slugify(title: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9\- ]', '', title).strip().lower().replace(' ', '-')
    return f"{datetime.data.today()}-{slug[:40]}"

def _read_prompt_file(name: str) -> str:
    path = PROMPTS_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {path}\n"
            f"Checked PROMPTS_DIR={PROMPTS_DIR}. "
            "Set PROMPTS_DIR env var if your layout differs."
        )
    return path.read_text(encoding="utf-8")

async def generate_post_service(topic: str | None):
    # pick a topic if none
    topic = topic or "Emerging AI tools for creators"
    
    # build prompt
    style = _read_prompt_file("style_guide.md")
    post  = _read_prompt_file("post_prompt.md")
    prompt = post.replace("{{TOPIC}}", topic) + "\n\nSTYLE_GUID:\n" + style
    return prompt

import asyncio
if __name__ == "__main__":
    prompt = asyncio.run(generate_post_service("Taylor Swift"))
    print(prompt)
    
    