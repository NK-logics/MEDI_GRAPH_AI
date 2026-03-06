from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.routes.auth import get_current_user
from app.services.intentRouter import route_intent

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(request: ChatRequest, user_id: str = Depends(get_current_user)):
    """
    Unified chat endpoint that handles both ingestion and retrieval
    """
    message = request.message
    
    # Route to appropriate pipeline based on intent
    result = route_intent(message, user_id)
    
    return result