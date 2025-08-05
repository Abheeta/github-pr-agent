from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Code Review Agent")
app.include_router(router)
