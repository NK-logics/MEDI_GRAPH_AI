from datetime import datetime, timedelta
import re
from typing import Dict, Tuple

class QueryClassifier:
    """
    Classifies user queries into retrieval intent types
    """
    
    # Intent patterns
    INTENT_PATTERNS = {
        "symptom_frequency": [
            r"how often", r"frequency", r"frequently", r"regularly",
            r"do i often", r"do i usually", r"how many times",
            r"does it happen often"
        ],
        "trigger_correlation": [
            r"what causes", r"what triggers", r"why do i get",
            r"what brings on", r"correlation", r"associated with",
            r"linked to", r"due to"
        ],
        "medication_history": [
            r"when did i take", r"did i take", r"have i taken",
            r"medication history", r"what medication", r"what did i take",
            r"took .* (medicine|medication|pill)"
        ],
        "multi_symptom": [
            r"and", r"together", r"at the same time",
            r"both", r"with.*and"
        ],
        "time_filtered": [
            r"last (week|month|day|monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
            r"yesterday", r"today", r"past week", r"previous",
            r"between", r"from.*to"
        ],
        "pattern_analysis": [
            r"pattern", r"trend", r"recurring", r"cycle",
            r"every (day|week|month)", r"repeating", r"regular interval"
        ]
    }
    
    # Time indicators
    TIME_INDICATORS = {
        "today": 0,
        "yesterday": 1,
        "last week": 7,
        "last month": 30,
        "last monday": "last_monday",
        "last tuesday": "last_tuesday",
        # Add more as needed
    }
    
    @classmethod
    def classify(cls, query: str) -> Dict[str, any]:
        """
        Classify the query intent and extract relevant parameters
        """
        query_lower = query.lower()
        
        # Default intent
        intent = "general_retrieval"
        confidence = 0.5
        params = {}
        
        # Check each intent pattern
        for intent_type, patterns in cls.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    intent = intent_type
                    confidence = 0.8
                    # Extract additional parameters
                    params = cls._extract_params(query_lower, intent_type)
                    break
            if intent != "general_retrieval":
                break
        
        # Extract time filters
        time_filter = cls._extract_time_filter(query_lower)
        if time_filter:
            params["time_filter"] = time_filter
        
        # Extract entities mentioned
        entities = cls._extract_entities(query_lower)
        if entities:
            params["entities"] = entities
        
        return {
            "intent": intent,
            "confidence": confidence,
            "params": params,
            "original_query": query
        }
    
    @classmethod
    def _extract_params(cls, query: str, intent: str) -> Dict:
        """Extract intent-specific parameters"""
        params = {}
        
        if intent == "symptom_frequency":
            # Extract symptom mentioned
            symptom_match = re.search(r"(headache|fever|cough|fatigue|nausea)", query)
            if symptom_match:
                params["symptom"] = symptom_match.group(1)
        
        elif intent == "trigger_correlation":
            # Extract symptom to find triggers for
            symptom_match = re.search(r"(headache|migraine|fever|cough)", query)
            if symptom_match:
                params["symptom"] = symptom_match.group(1)
        
        elif intent == "medication_history":
            # Extract medication mentioned
            med_match = re.search(r"(paracetamol|ibuprofen|aspirin|crocin)", query)
            if med_match:
                params["medication"] = med_match.group(1)
        
        return params
    
    @classmethod
    def _extract_time_filter(cls, query: str) -> Dict:
        """Extract time-based filters from query"""
        today = datetime.now().date()
        
        if "today" in query:
            return {"type": "specific", "date": today}
        elif "yesterday" in query:
            return {"type": "specific", "date": today - timedelta(days=1)}
        elif "last week" in query:
            return {"type": "range", "start": today - timedelta(days=7), "end": today}
        elif "last month" in query:
            return {"type": "range", "start": today - timedelta(days=30), "end": today}
        
        return None
    
    @classmethod
    def _extract_entities(cls, query: str) -> Dict:
        """Extract symptoms, triggers, medications from query"""
        from app.services.ingestion.entityDictionary import SYMPTOM_MAP, TRIGGER_MAP, MEDICATION_MAP
        
        entities = {
            "symptoms": [],
            "triggers": [],
            "medications": []
        }
        
        query_lower = query.lower()
        
        # Check for symptoms
        for canonical, variants in SYMPTOM_MAP.items():
            for variant in variants:
                if variant in query_lower:
                    entities["symptoms"].append(canonical)
                    break
        
        # Check for triggers
        for canonical, variants in TRIGGER_MAP.items():
            for variant in variants:
                if variant in query_lower:
                    entities["triggers"].append(canonical)
                    break
        
        # Check for medications
        for canonical, variants in MEDICATION_MAP.items():
            for variant in variants:
                if variant in query_lower:
                    entities["medications"].append(canonical)
                    break
        
        return {k: list(set(v)) for k, v in entities.items()}