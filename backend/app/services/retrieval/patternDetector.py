from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import Counter, defaultdict

class PatternDetector:
    """
    Detects patterns in health data
    """
    
    @staticmethod
    def detect_frequency_patterns(timeline_data: List[Dict]) -> Dict:
        """
        Detect frequency patterns in symptom occurrences
        """
        if not timeline_data:
            return {"pattern_detected": False, "message": "No data available"}
        
        # Group by symptom
        symptom_occurrences = defaultdict(list)
        for entry in timeline_data:
            symptom = entry.get("symptom")
            date = entry.get("date")
            if symptom and date:
                symptom_occurrences[symptom].append(date)
        
        patterns = {}
        for symptom, dates in symptom_occurrences.items():
            # Convert to datetime if needed
            parsed_dates = []
            for d in dates:
                if isinstance(d, str):
                    try:
                        parsed_dates.append(datetime.strptime(d, "%Y-%m-%d").date())
                    except:
                        continue
                else:
                    parsed_dates.append(d)
            
            if len(parsed_dates) < 2:
                patterns[symptom] = {
                    "frequency": "insufficient_data",
                    "occurrence_count": len(parsed_dates)
                }
                continue
            
            # Calculate gaps
            parsed_dates.sort()
            gaps = [(parsed_dates[i+1] - parsed_dates[i]).days 
                    for i in range(len(parsed_dates)-1)]
            
            avg_gap = sum(gaps) / len(gaps)
            
            # Determine frequency category
            if avg_gap <= 2:
                frequency = "daily"
            elif avg_gap <= 7:
                frequency = "weekly"
            elif avg_gap <= 14:
                frequency = "biweekly"
            elif avg_gap <= 30:
                frequency = "monthly"
            else:
                frequency = "occasional"
            
            # Check for cyclic patterns
            gap_counter = Counter(gaps)
            most_common_gap = gap_counter.most_common(1)[0] if gap_counter else (0, 0)
            
            patterns[symptom] = {
                "frequency": frequency,
                "average_gap_days": round(avg_gap, 1),
                "most_common_gap_days": most_common_gap[0],
                "total_occurrences": len(parsed_dates),
                "gaps": gaps,
                "cyclic_pattern_detected": most_common_gap[1] > len(gaps) * 0.3
            }
        
        return {
            "pattern_detected": bool(patterns),
            "patterns": patterns
        }
    
    @staticmethod
    def detect_correlations(symptom_data: List[Dict], trigger_data: List[Dict]) -> Dict:
        """
        Detect correlations between symptoms and triggers
        """
        # This would require more sophisticated analysis
        # For now, return basic co-occurrence stats
        return {
            "correlations_detected": False,
            "message": "Correlation analysis requires more sophisticated implementation"
        }
    
    @staticmethod
    def detect_seasonal_patterns(timeline_data: List[Dict]) -> Dict:
        """
        Detect seasonal patterns in symptoms
        """
        if not timeline_data:
            return {"seasonal_pattern_detected": False}
        
        # Group by month
        monthly_counts = defaultdict(int)
        for entry in timeline_data:
            date = entry.get("date")
            if date:
                if isinstance(date, str):
                    try:
                        date_obj = datetime.strptime(date, "%Y-%m-%d")
                        month = date_obj.strftime("%B")
                        monthly_counts[month] += 1
                    except:
                        continue
                else:
                    # Assume it's a date object
                    month = date.strftime("%B") if hasattr(date, "strftime") else "Unknown"
                    monthly_counts[month] += 1
        
        # Check if any month has significantly higher counts
        if monthly_counts:
            avg_count = sum(monthly_counts.values()) / len(monthly_counts)
            seasonal_months = [month for month, count in monthly_counts.items() 
                             if count > avg_count * 1.5]
            
            return {
                "seasonal_pattern_detected": len(seasonal_months) > 0,
                "monthly_distribution": dict(monthly_counts),
                "peak_months": seasonal_months
            }
        
        return {"seasonal_pattern_detected": False}