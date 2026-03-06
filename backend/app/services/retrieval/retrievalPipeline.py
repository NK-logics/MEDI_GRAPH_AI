import time
from typing import Dict, Any
from datetime import datetime

from app.services.retrieval.queryClassifier import QueryClassifier
from app.services.retrieval.graphQueries import GraphQueries
from app.services.retrieval.patternDetector import PatternDetector
from app.services.retrieval.temporalAnalyzer import TemporalAnalyzer
from app.services.retrieval.contextBuilder import ContextBuilder
from app.services.retrieval.responseFormatter import ResponseFormatter

class RetrievalPipeline:
    """
    Main retrieval pipeline orchestrator
    """
    
    def __init__(self):
        self.classifier = QueryClassifier()
        self.graph_queries = GraphQueries()
        self.pattern_detector = PatternDetector()
        self.temporal_analyzer = TemporalAnalyzer()
        self.context_builder = ContextBuilder()
        self.formatter = ResponseFormatter()
    
    def run(self, message: str, user_id: str) -> Dict:
        """
        Execute the retrieval pipeline
        """
        # Start timer
        start_time = time.time()
        
        # Step 1: Classify query intent
        query_classification = self.classifier.classify(message)
        
        # If not a retrieval intent, return early
        if query_classification["intent"] == "ingestion":
            return {
                "status": "not_retrieval",
                "message": "This appears to be a health logging query."
            }
        
        # Step 2: Extract time filters if present
        time_filter = self.temporal_analyzer.parse_time_reference(message)
        
        # Step 3: Execute appropriate graph queries based on intent
        retrieved_data = self._execute_queries(
            user_id, 
            query_classification,
            time_filter
        )
        
        # Step 4: Detect patterns if needed
        if query_classification["intent"] in ["pattern_analysis", "symptom_frequency"]:
            if retrieved_data.get("timeline"):
                patterns = self.pattern_detector.detect_frequency_patterns(
                    retrieved_data["timeline"]
                )
                retrieved_data["patterns"] = patterns
        
        # Step 5: Apply temporal filtering
        if time_filter and retrieved_data.get("timeline"):
            retrieved_data["timeline"] = self.temporal_analyzer.filter_by_time(
                retrieved_data["timeline"],
                time_filter
            )
            retrieved_data["time_filter_applied"] = time_filter
        
        # Step 6: Calculate temporal statistics
        if retrieved_data.get("timeline"):
            retrieved_data["temporal_stats"] = self.temporal_analyzer.calculate_temporal_statistics(
                retrieved_data["timeline"]
            )
        
        # Step 7: Build context
        context = self.context_builder.build_context(
            query_classification,
            retrieved_data
        )
        
        # Add retrieval time
        context["retrieval_time_ms"] = round((time.time() - start_time) * 1000, 2)
        
        # Step 8: Format response
        response = self.formatter.format_response(context)
        
        # Step 9: Add status
        response["status"] = "success"
        response["user_id"] = user_id
        
        return response
    
    def _execute_queries(self, user_id: str, 
                         query_classification: Dict,
                         time_filter: Dict = None) -> Dict:
        """
        Execute appropriate graph queries based on intent
        """
        intent = query_classification["intent"]
        params = query_classification.get("params", {})
        
        retrieved_data = {}
        
        # Convert time filter to date range if needed
        start_date = None
        end_date = None
        
        if time_filter:
            if time_filter["type"] == "range":
                start_date = time_filter["start"]
                end_date = time_filter["end"]
            elif time_filter["type"] == "specific":
                start_date = time_filter["date"]
                end_date = time_filter["date"]
        
        # Execute intent-specific queries
        if intent == "symptom_frequency":
            symptom = params.get("entities", {}).get("symptoms", [None])[0]
            retrieved_data["frequency"] = self.graph_queries.get_symptom_frequency(
                user_id, 
                symptom=symptom,
                start_date=start_date,
                end_date=end_date
            )
            
            # Also get timeline for pattern detection
            retrieved_data["timeline"] = self.graph_queries.get_symptom_timeline(
                user_id,
                symptom=symptom
            )
        
        elif intent == "trigger_correlation":
            symptom = params.get("entities", {}).get("symptoms", [None])[0]
            retrieved_data["triggers"] = self.graph_queries.get_trigger_correlation(
                user_id,
                symptom=symptom
            )
        
        elif intent == "medication_history":
            medication = params.get("entities", {}).get("medications", [None])[0]
            retrieved_data["medications"] = self.graph_queries.get_medication_history(
                user_id,
                medication=medication,
                start_date=start_date,
                end_date=end_date
            )
        
        elif intent == "multi_symptom":
            symptoms = params.get("entities", {}).get("symptoms", [])
            if symptoms:
                retrieved_data["multi_symptom"] = self.graph_queries.get_multi_symptom_occurrences(
                    user_id,
                    symptoms
                )
        
        elif intent == "pattern_analysis":
            symptom = params.get("entities", {}).get("symptoms", [None])[0]
            if symptom:
                retrieved_data["patterns"] = self.graph_queries.get_symptom_patterns(
                    user_id,
                    symptom
                )
            else:
                # Get all symptoms for pattern analysis
                retrieved_data["timeline"] = self.graph_queries.get_symptom_timeline(
                    user_id
                )
        
        else:  # General retrieval or time_filtered
            retrieved_data["timeline"] = self.graph_queries.get_symptom_timeline(
                user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            retrieved_data["medications"] = self.graph_queries.get_medication_history(
                user_id,
                start_date=start_date,
                end_date=end_date
            )
        
        return retrieved_data

# Singleton instance
_retrieval_pipeline = None

def get_retrieval_pipeline():
    global _retrieval_pipeline
    if _retrieval_pipeline is None:
        _retrieval_pipeline = RetrievalPipeline()
    return _retrieval_pipeline

def run_retrieval_pipeline(message: str, user_id: str) -> Dict:
    """
    Convenience function to run the retrieval pipeline
    """
    pipeline = get_retrieval_pipeline()
    return pipeline.run(message, user_id)