from typing import Dict, Any
from datetime import datetime

class ResponseFormatter:
    """
    Formats retrieval results into user-friendly responses
    """
    
    @staticmethod
    def format_response(context: Dict) -> Dict:
        """
        Format the context into a final response
        """
        intent = context["query_info"]["intent"]
        
        # Build the response based on intent
        if intent == "symptom_frequency":
            response = ResponseFormatter._format_frequency_response(context)
        elif intent == "trigger_correlation":
            response = ResponseFormatter._format_trigger_response(context)
        elif intent == "medication_history":
            response = ResponseFormatter._format_medication_response(context)
        elif intent == "multi_symptom":
            response = ResponseFormatter._format_multi_symptom_response(context)
        elif intent == "pattern_analysis":
            response = ResponseFormatter._format_pattern_response(context)
        elif intent == "time_filtered":
            response = ResponseFormatter._format_time_filtered_response(context)
        else:
            response = ResponseFormatter._format_general_response(context)
        
        # Add metadata
        response["metadata"] = {
            "retrieval_time_ms": context.get("retrieval_time_ms", 0),
            "citations_count": len(context.get("citations", [])),
            "data_points": ResponseFormatter._count_data_points(context)
        }
        
        # Add citations if available
        if context.get("citations"):
            response["citations"] = context["citations"]
        
        return response
    
    @staticmethod
    def _format_frequency_response(context: Dict) -> Dict:
        """Format frequency response"""
        summary = context.get("summary", {})
        
        if "message" in summary:
            return {
                "type": "symptom_frequency",
                "message": summary["message"]
            }
        
        # Build natural language response
        symptom_breakdown = summary.get("symptom_breakdown", [])
        
        if not symptom_breakdown:
            return {
                "type": "symptom_frequency",
                "message": "I don't have any symptom data to analyze frequency."
            }
        
        # Find most frequent symptom
        most_frequent = max(symptom_breakdown, key=lambda x: x["frequency"])
        
        message_parts = [
            f"Based on your health records, here's your symptom frequency analysis:"
        ]
        
        for item in symptom_breakdown:
            freq = item["frequency"]
            symptom = item["symptom"]
            
            if freq > 5:
                message_parts.append(f"• {symptom.capitalize()}: You've reported this {freq} times, which is quite frequent.")
            elif freq > 2:
                message_parts.append(f"• {symptom.capitalize()}: You've reported this {freq} times.")
            else:
                message_parts.append(f"• {symptom.capitalize()}: Reported {freq} time(s).")
        
        message_parts.append(f"\nYour most frequently reported symptom is {most_frequent['symptom']}.")
        
        return {
            "type": "symptom_frequency",
            "message": " ".join(message_parts),
            "data": summary
        }
    
    @staticmethod
    def _format_trigger_response(context: Dict) -> Dict:
        """Format trigger correlation response"""
        summary = context.get("summary", {})
        
        if "message" in summary:
            return {
                "type": "trigger_correlation",
                "message": summary["message"]
            }
        
        trigger_analysis = summary.get("trigger_analysis", [])
        
        if not trigger_analysis:
            return {
                "type": "trigger_correlation",
                "message": "I don't have enough data to analyze triggers yet."
            }
        
        message_parts = ["Here's what I found about your symptom triggers:"]
        
        for analysis in trigger_analysis:
            symptom = analysis["symptom"]
            triggers = analysis["associated_triggers"]
            occurrences = analysis["occurrences"]
            
            if triggers:
                trigger_list = ", ".join(triggers[:3])
                message_parts.append(f"• For {symptom} ({occurrences} occurrences), associated triggers include: {trigger_list}")
            else:
                message_parts.append(f"• {symptom} has been reported {occurrences} times, but no specific triggers were recorded.")
        
        return {
            "type": "trigger_correlation",
            "message": " ".join(message_parts),
            "data": summary
        }
    
    @staticmethod
    def _format_medication_response(context: Dict) -> Dict:
        """Format medication history response"""
        summary = context.get("summary", {})
        
        if "message" in summary:
            return {
                "type": "medication_history",
                "message": summary["message"]
            }
        
        medications = summary.get("medications_taken", [])
        
        if not medications:
            return {
                "type": "medication_history",
                "message": "I don't have any medication records for you yet."
            }
        
        message_parts = ["Your medication history shows:"]
        
        for med in medications:
            message_parts.append(f"• {med['medication'].capitalize()}: taken {med['times_taken']} time(s)")
        
        return {
            "type": "medication_history",
            "message": " ".join(message_parts),
            "data": summary
        }
    
    @staticmethod
    def _format_multi_symptom_response(context: Dict) -> Dict:
        """Format multi-symptom response"""
        summary = context.get("summary", {})
        
        if "message" in summary:
            return {
                "type": "multi_symptom",
                "message": summary["message"]
            }
        
        episodes = summary.get("episodes", [])
        
        if not episodes:
            return {
                "type": "multi_symptom",
                "message": "I haven't found any instances where multiple symptoms occurred together."
            }
        
        message_parts = [f"I found {summary.get('co_occurring_episodes', 0)} instances where multiple symptoms occurred together:"]
        
        for episode in episodes[:3]:  # Show top 3
            symptoms = ", ".join(episode.get("symptoms", []))
            message_parts.append(f"• On {episode.get('date')}: {symptoms}")
        
        if len(episodes) > 3:
            message_parts.append(f"and {len(episodes) - 3} more occurrences.")
        
        return {
            "type": "multi_symptom",
            "message": " ".join(message_parts),
            "data": summary
        }
    
    @staticmethod
    def _format_pattern_response(context: Dict) -> Dict:
        """Format pattern analysis response"""
        summary = context.get("summary", {})
        
        if "message" in summary:
            return {
                "type": "pattern_analysis",
                "message": summary["message"]
            }
        
        analysis = summary.get("analysis", {})
        
        if not analysis:
            return {
                "type": "pattern_analysis",
                "message": "I couldn't detect any clear patterns in your health data yet."
            }
        
        message_parts = ["Pattern analysis of your health data reveals:"]
        
        for symptom, pattern in analysis.items():
            freq = pattern.get("frequency", "unknown")
            avg_gap = pattern.get("average_gap_days", 0)
            cyclic = pattern.get("cyclic", False)
            
            message_parts.append(f"• {symptom.capitalize()}: {freq} pattern (every {avg_gap:.0f} days on average)")
            if cyclic:
                message_parts[-1] += " — appears to be cyclic!"
        
        return {
            "type": "pattern_analysis",
            "message": " ".join(message_parts),
            "data": summary
        }
    
    @staticmethod
    def _format_time_filtered_response(context: Dict) -> Dict:
        """Format time-filtered response"""
        summary = context.get("summary", {})
        
        if "message" in summary:
            return {
                "type": "time_filtered",
                "message": summary["message"]
            }
        
        time_range = summary.get("time_range", {})
        total = summary.get("total_occurrences", 0)
        breakdown = summary.get("symptom_breakdown", {})
        
        range_desc = "the specified period"
        if isinstance(time_range, dict):
            if time_range.get("type") == "range":
                start = time_range.get("start", "unknown")
                end = time_range.get("end", "unknown")
                range_desc = f"from {start} to {end}"
            elif time_range.get("type") == "specific":
                range_desc = f"on {time_range.get('date', 'unknown')}"
        
        message_parts = [f"For {range_desc}, I found {total} health event(s):"]
        
        for symptom, count in breakdown.items():
            message_parts.append(f"• {symptom.capitalize()}: {count} time(s)")
        
        return {
            "type": "time_filtered",
            "message": " ".join(message_parts),
            "data": summary
        }
    
    @staticmethod
    def _format_general_response(context: Dict) -> Dict:
        """Format general response for other queries"""
        return {
            "type": "general",
            "message": "I've analyzed your health data based on your query.",
            "data": context.get("summary", {})
        }
    
    @staticmethod
    def _count_data_points(context: Dict) -> int:
        """Count total data points in the context"""
        count = 0
        data = context.get("data", {})
        
        for key, value in data.items():
            if isinstance(value, list):
                count += len(value)
            elif isinstance(value, dict):
                count += len(value)
        
        return count