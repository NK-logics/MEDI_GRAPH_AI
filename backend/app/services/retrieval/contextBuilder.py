from typing import Dict, Any, List
from datetime import datetime

class ContextBuilder:
    """
    Builds structured context from retrieved data
    """
    
    @staticmethod
    def build_context(query_classification: Dict, 
                      retrieved_data: Dict) -> Dict:
        """
        Build a structured context object for response generation
        """
        intent = query_classification.get("intent")
        params = query_classification.get("params", {})
        
        context = {
            "query_info": {
                "original_query": query_classification.get("original_query"),
                "intent": intent,
                "confidence": query_classification.get("confidence"),
                "params": params
            },
            "data": retrieved_data,
            "summary": {},
            "citations": [],
            "retrieval_time": datetime.now().isoformat()
        }
        
        # Build intent-specific summaries
        if intent == "symptom_frequency":
            context["summary"] = ContextBuilder._summarize_frequency(retrieved_data)
        elif intent == "trigger_correlation":
            context["summary"] = ContextBuilder._summarize_triggers(retrieved_data)
        elif intent == "medication_history":
            context["summary"] = ContextBuilder._summarize_medications(retrieved_data)
        elif intent == "multi_symptom":
            context["summary"] = ContextBuilder._summarize_multi_symptom(retrieved_data)
        elif intent == "pattern_analysis":
            context["summary"] = ContextBuilder._summarize_patterns(retrieved_data)
        elif intent == "time_filtered":
            context["summary"] = ContextBuilder._summarize_time_filtered(retrieved_data)
        
        # Extract citations
        context["citations"] = ContextBuilder._extract_citations(retrieved_data)
        
        return context
    
    @staticmethod
    def _summarize_frequency(data: Dict) -> Dict:
        """Summarize frequency data"""
        frequency_data = data.get("frequency", [])
        if not frequency_data:
            return {"message": "No frequency data available"}
        
        summary = {
            "total_symptoms_reported": len(frequency_data),
            "symptom_breakdown": []
        }
        
        for item in frequency_data:
            summary["symptom_breakdown"].append({
                "symptom": item.get("symptom"),
                "frequency": item.get("frequency", 0),
                "first_reported": min(item.get("dates", [])) if item.get("dates") else None,
                "last_reported": max(item.get("dates", [])) if item.get("dates") else None
            })
        
        return summary
    
    @staticmethod
    def _summarize_triggers(data: Dict) -> Dict:
        """Summarize trigger correlation data"""
        trigger_data = data.get("triggers", [])
        if not trigger_data:
            return {"message": "No trigger data available"}
        
        summary = {
            "trigger_analysis": []
        }
        
        for item in trigger_data:
            summary["trigger_analysis"].append({
                "symptom": item.get("symptom"),
                "associated_triggers": item.get("triggers", []),
                "occurrences": item.get("occurrences", 0)
            })
        
        return summary
    
    @staticmethod
    def _summarize_medications(data: Dict) -> Dict:
        """Summarize medication history"""
        med_data = data.get("medications", [])
        if not med_data:
            return {"message": "No medication data available"}
        
        summary = {
            "medications_taken": []
        }
        
        for item in med_data:
            summary["medications_taken"].append({
                "medication": item.get("medication"),
                "times_taken": item.get("times_taken", 0),
                "records_count": len(item.get("records", []))
            })
        
        return summary
    
    @staticmethod
    def _summarize_multi_symptom(data: Dict) -> Dict:
        """Summarize multi-symptom occurrences"""
        multi_data = data.get("multi_symptom", [])
        if not multi_data:
            return {"message": "No multi-symptom data available"}
        
        summary = {
            "co_occurring_episodes": len(multi_data),
            "episodes": []
        }
        
        for item in multi_data[:5]:  # Limit to 5 examples
            summary["episodes"].append({
                "date": item.get("date"),
                "symptoms": item.get("symptoms_present", []),
                "sources": item.get("sources", [])[:2]  # Limit sources
            })
        
        return summary
    
    @staticmethod
    def _summarize_patterns(data: Dict) -> Dict:
        """Summarize pattern analysis"""
        patterns = data.get("patterns", {})
        if not patterns:
            return {"message": "No pattern data available"}
        
        summary = {
            "patterns_detected": patterns.get("pattern_detected", False),
            "analysis": {}
        }
        
        symptom_patterns = patterns.get("patterns", {})
        for symptom, pattern in symptom_patterns.items():
            summary["analysis"][symptom] = {
                "frequency": pattern.get("frequency", "unknown"),
                "average_gap_days": pattern.get("average_gap_days", 0),
                "cyclic": pattern.get("cyclic_pattern_detected", False)
            }
        
        return summary
    
    @staticmethod
    def _summarize_time_filtered(data: Dict) -> Dict:
        """Summarize time-filtered data"""
        timeline = data.get("timeline", [])
        time_filter = data.get("time_filter_applied", {})
        
        if not timeline:
            return {"message": "No data in the specified time range"}
        
        # Group by symptom
        symptom_counts = {}
        for item in timeline:
            symptom = item.get("symptom")
            if symptom:
                symptom_counts[symptom] = symptom_counts.get(symptom, 0) + 1
        
        return {
            "time_range": time_filter,
            "total_occurrences": len(timeline),
            "symptom_breakdown": symptom_counts,
            "first_in_range": timeline[-1].get("date") if timeline else None,
            "last_in_range": timeline[0].get("date") if timeline else None
        }
    
    @staticmethod
    def _extract_citations(data: Dict) -> List[Dict]:
        """
        Extract citations from retrieved data
        Format: Node ID, Snippet, Score, Retrieval Time
        """
        citations = []
        
        # Extract from various data structures
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        # Look for source text
                        source = item.get("source") or item.get("source_text")
                        if source:
                            citations.append({
                                "node_id": item.get("symptom") or item.get("medication") or "unknown",
                                "snippet": source[:100] + "..." if len(source) > 100 else source,
                                "score": 1.0,  # Default score, could be calculated
                                "retrieval_time": datetime.now().isoformat()
                            })
        
        return citations[:10]  # Limit to 10 citations