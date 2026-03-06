from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.db.neo4j_driver import get_session

class GraphQueries:
    """
    Handles all Neo4j queries for the retrieval pipeline
    """
    
    @staticmethod
    def get_symptom_frequency(user_id: str, symptom: Optional[str] = None, 
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> List[Dict]:
        """
        Get frequency of symptoms for a user
        """
        with get_session() as session:
            # Base query
            query = """
            MATCH (u:User {id: $user_id})-[r:HAS_SYMPTOM]->(s:Symptom)
            WHERE 1=1
            """
            
            params = {"user_id": user_id}
            
            # Add filters
            if symptom:
                query += " AND s.name = $symptom"
                params["symptom"] = symptom
            
            if start_date:
                query += " AND r.reported_at >= $start_date"
                params["start_date"] = str(start_date)
            
            if end_date:
                query += " AND r.reported_at <= $end_date"
                params["end_date"] = str(end_date)
            
            # Add return clause
            query += """
            RETURN s.name AS symptom, 
                   count(r) AS frequency,
                   collect(DISTINCT r.reported_at) AS dates,
                   collect(DISTINCT r.source_text) AS sources
            ORDER BY frequency DESC
            """
            
            result = session.run(query, **params)
            return [dict(record) for record in result]
    
    @staticmethod
    def get_trigger_correlation(user_id: str, symptom: Optional[str] = None) -> List[Dict]:
        """
        Find correlations between triggers and symptoms
        """
        with get_session() as session:
            query = """
            MATCH (u:User {id: $user_id})-[hs:HAS_SYMPTOM]->(s:Symptom)
            OPTIONAL MATCH (u)-[tb:TRIGGERED_BY]->(t:Trigger)
            
            WITH u, s, hs, COLLECT(DISTINCT t.name) AS triggers
            WHERE s.name = $symptom OR $symptom IS NULL
            
            RETURN s.name AS symptom,
                   triggers,
                   COUNT(hs) AS occurrences,
                   COLLECT(DISTINCT hs.reported_at) AS dates
            ORDER BY occurrences DESC
            """
            
            params = {"user_id": user_id, "symptom": symptom}
            result = session.run(query, **params)
            return [dict(record) for record in result]
    
    @staticmethod
    def get_medication_history(user_id: str, medication: Optional[str] = None,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[Dict]:
        """
        Get medication usage history
        """
        with get_session() as session:
            query = """
            MATCH (u:User {id: $user_id})-[r:TAKES_MEDICATION]->(m:Medication)
            WHERE 1=1
            """
            
            params = {"user_id": user_id}
            
            if medication:
                query += " AND m.name = $medication"
                params["medication"] = medication
            
            # Note: TAKES_MEDICATION might not have timestamps yet
            # You might need to add them similar to HAS_SYMPTOM
            
            query += """
            RETURN m.name AS medication,
                   COUNT(r) AS times_taken,
                   COLLECT(r) AS records
            ORDER BY times_taken DESC
            """
            
            result = session.run(query, **params)
            return [dict(record) for record in result]
    
    @staticmethod
    def get_symptom_timeline(user_id: str, symptom: Optional[str] = None,
                              days: int = 30) -> List[Dict]:
        """
        Get symptom occurrences over time
        """
        with get_session() as session:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            query = """
            MATCH (u:User {id: $user_id})-[r:HAS_SYMPTOM]->(s:Symptom)
            WHERE date(r.reported_at) >= date($start_date)
              AND date(r.reported_at) <= date($end_date)
            """
            
            params = {
                "user_id": user_id,
                "start_date": str(start_date.date()),
                "end_date": str(end_date.date())
            }
            
            if symptom:
                query += " AND s.name = $symptom"
                params["symptom"] = symptom
            
            query += """
            RETURN s.name AS symptom,
                   r.reported_at AS date,
                   r.source_text AS source
            ORDER BY r.reported_at DESC
            """
            
            result = session.run(query, **params)
            return [dict(record) for record in result]
    
    @staticmethod
    def get_multi_symptom_occurrences(user_id: str, symptoms: List[str]) -> List[Dict]:
        """
        Find occurrences where multiple symptoms were reported together
        """
        with get_session() as session:
            query = """
            MATCH (u:User {id: $user_id})-[r:HAS_SYMPTOM]->(s:Symptom)
            WHERE s.name IN $symptoms
            
            WITH r.reported_at AS date, COLLECT(s.name) AS symptoms_present
            WHERE SIZE(symptoms_present) >= $min_symptoms
            
            RETURN date, symptoms_present, COLLECT(r.source_text) AS sources
            ORDER BY date DESC
            """
            
            params = {
                "user_id": user_id,
                "symptoms": symptoms,
                "min_symptoms": min(2, len(symptoms))
            }
            
            result = session.run(query, **params)
            return [dict(record) for record in result]
    
    @staticmethod
    def get_symptom_patterns(user_id: str, symptom: str) -> Dict:
        """
        Analyze patterns in symptom occurrences
        """
        with get_session() as session:
            # Get all occurrences with timestamps
            query = """
            MATCH (u:User {id: $user_id})-[r:HAS_SYMPTOM]->(s:Symptom {name: $symptom})
            RETURN r.reported_at AS date, r.source_text AS source
            ORDER BY r.reported_at
            """
            
            params = {"user_id": user_id, "symptom": symptom}
            result = session.run(query, **params)
            
            occurrences = [dict(record) for record in result]
            
            # Calculate patterns
            if len(occurrences) < 2:
                return {
                    "symptom": symptom,
                    "occurrences": occurrences,
                    "pattern_detected": False,
                    "message": "Not enough data for pattern analysis"
                }
            
            # Convert dates to datetime objects
            dates = []
            for occ in occurrences:
                try:
                    date_str = occ.get("date")
                    if date_str:
                        # Handle different date formats
                        if isinstance(date_str, str):
                            dates.append(datetime.strptime(date_str, "%Y-%m-%d").date())
                        else:
                            # Assume it's already a date object
                            dates.append(date_str)
                except:
                    continue
            
            if len(dates) < 2:
                return {
                    "symptom": symptom,
                    "occurrences": occurrences,
                    "pattern_detected": False,
                    "message": "Could not parse dates for pattern analysis"
                }
            
            # Calculate gaps between occurrences
            gaps = []
            for i in range(1, len(dates)):
                gap = (dates[i] - dates[i-1]).days
                gaps.append(gap)
            
            # Detect patterns
            from collections import Counter
            gap_counter = Counter(gaps)
            
            # Check for weekly pattern (7 days)
            weekly_pattern = any(gap % 7 == 0 and gap > 0 for gap in gaps)
            
            # Most common gap
            if gap_counter:
                most_common_gap = gap_counter.most_common(1)[0]
            else:
                most_common_gap = (0, 0)
            
            return {
                "symptom": symptom,
                "total_occurrences": len(occurrences),
                "occurrences": occurrences,
                "gaps_between_occurrences": gaps,
                "average_gap_days": sum(gaps) / len(gaps) if gaps else 0,
                "most_common_gap_days": most_common_gap[0],
                "most_common_gap_frequency": most_common_gap[1],
                "weekly_pattern_detected": weekly_pattern,
                "pattern_detected": len(set(gaps)) < len(gaps)  # Some gaps repeat
            }