from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.routes.auth import get_current_user
from app.services.intentRouter import detectIntent
from app.services.ingestion.ingestionPipeline import run_ingestion_pipeline
# from app.services.retrieval.retrieval_pipeline import run_retrieval_pipeline

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")

def chat(request: ChatRequest, user_id: str = Depends(get_current_user)):

    message = request.message

    intent = detectIntent(message)

    if intent == "ingestion":
        return run_ingestion_pipeline(message, user_id)
    
    # if intent == "retrieval":
    #     return run_retrieval_pipeline(message, user_id)
    
    return{
        "status": "unknown_intent"
    }