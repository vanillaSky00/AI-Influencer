from fastapi import APIRouter
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from celery.result import AsyncResult

from backend.services.worker import app, avatar_post, avatar_reply


# load_dotenv()
router = APIRouter()


@router.post("/")
def root():
    return {"message": "🐱 Cat Avatar is online!"}

@router.post("/avatar/reply")
def create_reply(prompt: str):
    task = avatar_reply.delay(prompt)
    return {"task_id": task.id, "status": "queued"}

@router.post("/avatar/post")
def create_reply(prompt: str):
    task = avatar_post.delay(prompt)
    return {"task_id": task.id, "status": "queued"}


@router.post("/tasks/{task_id}")
def get_task_status(task_id: str):
    
    result = AsyncResult(task_id, app=app)
    
    if result == "PENDING":
        return {"task_id": task_id, "status": "pending"}

    if result == "FAILURE":
        return {"task_id": task_id, "status": "failed", "error": str(result.result)}
    
    if result == "SUCCESS":
        return {"task_id": task_id, "status": "success", "data": result.result}
    
    return {"task_id": task_id, "status": result.state}
        




