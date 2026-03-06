from typing import Dict
from .retrieval.retrievalPipeline import run_retrieval_pipeline

def detectIntent(message: str) -> str:
    """
    Detect if the message is for ingestion or retrieval
    """
    message = message.lower()

    # question indicators
    question_words = [
        "what",
        "when",
        "how",
        "did",
        "which",
        "show",
        "list",
        "do i",
        "did i",
        "have i",
        "when did",
        "tell me about",
        "show me",
        "find"
    ]

    # Check for retrieval (questions)
    if "?" in message:
        return "retrieval"

    for word in question_words:
        if message.startswith(word):
            return "retrieval"
    
    # Check for specific retrieval patterns
    retrieval_patterns = [
        "frequency",
        "how often",
        "what causes",
        "correlation",
        "history",
        "pattern",
        "together",
        "last week",
        "last month"
    ]
    
    for pattern in retrieval_patterns:
        if pattern in message:
            return "retrieval"

    # Default to ingestion for health logging
    return "ingestion"

def route_intent(message: str, user_id: str) -> Dict:
    """
    Route the message to appropriate pipeline based on intent
    """
    intent = detectIntent(message)
    
    if intent == "ingestion":
        from .ingestion.ingestionPipeline import run_ingestion_pipeline
        return run_ingestion_pipeline(message, user_id)
    
    elif intent == "retrieval":
        return run_retrieval_pipeline(message, user_id)
    
    else:
        return {
            "status": "unknown_intent",
            "message": "I couldn't understand if you're logging health data or asking a question."
        }