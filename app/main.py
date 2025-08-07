from fastapi import FastAPI
from app.api.routes import router

# Entry for the app, create fastapi app
app = FastAPI(title="GitHub PR Analyzer")
app.include_router(router)
