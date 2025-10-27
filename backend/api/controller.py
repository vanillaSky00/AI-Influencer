from fastapi import APIRouter
from fastapi.responses import JSONResponse
from api.schemas import PromptIn
from dotenv import load_dotenv
from celery.result import AsyncResult

from services.worker import app as celery_app, avatar_post, avatar_reply

# load_dotenv()
router = APIRouter()


@router.post("/")
def root():
    return {"message": "🐱 Cat Avatar is online!"}

@router.post("/avatar/reply")
def create_reply(body: PromptIn):
    task = avatar_reply.delay(body.prompt)
    return {"task_id": task.id, "status": "queued"}

@router.post("/avatar/post")
def create_reply(body: PromptIn):
    task = avatar_post.delay(body.prompt)
    return {"task_id": task.id, "status": "queued"}

@router.get("/tasks/{task_id}")
def get_task_status(task_id: str):
    
    result = AsyncResult(task_id, app=celery_app)
    
    if result.state == "PENDING":
        return {"task_id": task_id, "status": "pending"}

    if result.state == "FAILURE":
        return {"task_id": task_id, "status": "failed", "error": str(result.result)}
    
    if result.state == "SUCCESS":
        return {"task_id": task_id, "status": "success", "data": result.result}
    
    return {"task_id": task_id, "status": result.state}
        




