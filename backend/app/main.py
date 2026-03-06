from fastapi import FastAPI
from app.routes.chat import router as chat_router


app = FastAPI()

@app.get("/")
def home():
    return {"message": "MediGraph API Running"}

app.include_router(chat_router)

