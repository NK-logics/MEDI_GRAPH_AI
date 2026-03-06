from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re

class TemporalAnalyzer:
    """
    Analyzes temporal aspects of health data
    """
    
    @staticmethod
    def parse_time_reference(query: str) -> Optional[Dict]:
        """
        Parse time references from natural language queries
        """
        query_lower = query.lower()
        today = datetime.now().date()
        
        # Absolute dates
        date_patterns = [
            (r"(\d{4}-\d{2}-\d{2})", lambda m: m.group(1)),  # YYYY-MM-DD
            (r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", lambda m: f"{m.group(3)}-{m.group(2)}-{m.group(1)}"),  # DD/MM/YYYY
        ]
        
        for pattern, formatter in date_patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    date_str = formatter(match)
                    return {
                        "type": "specific",
                        "date": datetime.strptime(date_str, "%Y-%m-%d").date()
                    }
                except:
                    pass
        
        # Relative time references
        if "today" in query_lower:
            return {"type": "specific", "date": today}
        
        if "yesterday" in query_lower:
            return {"type": "specific", "date": today - timedelta(days=1)}
        
        # Last X days/weeks/months
        last_pattern = r"last (\d+) (day|days|week|weeks|month|months)"
        match = re.search(last_pattern, query_lower)
        if match:
            number = int(match.group(1))
            unit = match.group(2)
            
            if unit.startswith("day"):
                delta = timedelta(days=number)
            elif unit.startswith("week"):
                delta = timedelta(weeks=number)
            elif unit.startswith("month"):
                delta = timedelta(days=number * 30)  # Approximate
            
            return {
                "type": "range",
                "start": today - delta,
                "end": today
            }
        
        # Day of week references
        days = ["monday", "tuesday", "wednesday", "thursday", 
                "friday", "saturday", "sunday"]
        
        for day in days:
            if f"last {day}" in query_lower:
                # Find the most recent occurrence of that day
                days_ago = (today.weekday() - days.index(day)) % 7
                if days_ago == 0:
                    days_ago = 7
                target_date = today - timedelta(days=days_ago)
                return {"type": "specific", "date": target_date}
        
        return None
    
    @staticmethod
    def filter_by_time(data: List[Dict], 
                       time_filter: Optional[Dict]) -> List[Dict]:
        """
        Filter data based on time constraints
        """
        if not time_filter or not data:
            return data
        
        filtered = []
        
        for item in data:
            item_date = item.get("date") or item.get("reported_at")
            if not item_date:
                filtered.append(item)
                continue
            
            # Parse date
            if isinstance(item_date, str):
                try:
                    item_date = datetime.strptime(item_date, "%Y-%m-%d").date()
                except:
                    filtered.append(item)
                    continue
            
            if time_filter["type"] == "specific":
                if item_date == time_filter["date"]:
                    filtered.append(item)
            
            elif time_filter["type"] == "range":
                if time_filter["start"] <= item_date <= time_filter["end"]:
                    filtered.append(item)
            
            elif time_filter["type"] == "before":
                if item_date <= time_filter["date"]:
                    filtered.append(item)
            
            elif time_filter["type"] == "after":
                if item_date >= time_filter["date"]:
                    filtered.append(item)
            
            else:
                filtered.append(item)
        
        return filtered
    
    @staticmethod
    def calculate_temporal_statistics(data: List[Dict]) -> Dict:
        """
        Calculate temporal statistics from the data
        """
        if not data:
            return {}
        
        # Extract dates
        dates = []
        for item in data:
            date_val = item.get("date") or item.get("reported_at")
            if date_val:
                if isinstance(date_val, str):
                    try:
                        dates.append(datetime.strptime(date_val, "%Y-%m-%d").date())
                    except:
                        continue
                else:
                    dates.append(date_val)
        
        if len(dates) < 2:
            return {
                "first_occurrence": min(dates) if dates else None,
                "last_occurrence": max(dates) if dates else None,
                "total_occurrences": len(dates)
            }
        
        dates.sort()
        
        # Calculate gaps
        gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        
        return {
            "first_occurrence": dates[0],
            "last_occurrence": dates[-1],
            "total_occurrences": len(dates),
            "timespan_days": (dates[-1] - dates[0]).days,
            "average_gap_days": sum(gaps) / len(gaps),
            "min_gap_days": min(gaps),
            "max_gap_days": max(gaps),
            "frequency_per_month": len(dates) * 30 / max((dates[-1] - dates[0]).days, 1)
        }