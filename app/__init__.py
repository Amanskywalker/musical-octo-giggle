from fastapi import FastAPI
from app.main import router

app = FastAPI()
app.include_router(router)