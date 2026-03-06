from fastapi import APIRouter
from pydantic import BaseModel

from app.services.intentRouter import detectIntent
from app.services.ingestion.ingestionPipeline import run_ingestion_pipeline
# from app.services.retrieval.retrieval_pipeline import run_retrieval_pipeline

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    userId: str

@router.post("/chat")

def chat(request: ChatRequest):

    message = request.message
    user_id = request.userId

    intent = detectIntent(message)

    if intent == "ingestion":
        return run_ingestion_pipeline(message, user_id)
    
    # if intent == "retrieval":
    #     return run_retrieval_pipeline(message, user_id)
    
    return{
        "status": "unknown_intent"
    }