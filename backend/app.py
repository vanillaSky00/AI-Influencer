from fastapi import FastAPI
from api.controller import router as controller_router

app = FastAPI(title="Cat Avatar API", version="1.0")

app.include_router(controller_router, prefix="/api")