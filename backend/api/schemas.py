from pydantic import BaseModel

class PromptIn(BaseModel):
    prompt: str
