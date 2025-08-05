from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="GitHub PR Analyzer")
app.include_router(router)
