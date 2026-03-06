from app.db.neo4j_driver import get_session
from datetime import datetime

def insert_symptoms(user_id, symptoms, source_text, reported_date):

    session = get_session()

    for symptom in symptoms:

        query = """
        MERGE (u:User {id:$user_id})
        MERGE (s:Symptom {name:$symptom})

        MERGE (u)-[:HAS_SYMPTOM {
            reported_at: $reported_date,
            source_text: $source_text,
            created_at: datetime()
        }]->(s)
        """

        session.run(
            query,
            user_id=user_id,
            symptom=symptom,
            source_text=source_text,
            reported_date=str(reported_date)
        )

def insert_triggers(user_id, triggers):

    session = get_session()

    for trigger in triggers:

        query = """
        MERGE (u:User {id:$user_id})

        MERGE (t:Trigger {name:$trigger})

        MERGE (u)-[:TRIGGERED_BY]->(t)
        """

        session.run(
            query,
            user_id=user_id,
            trigger=trigger
        )


def insert_medications(user_id, medications):

    session = get_session()

    for medication in medications:

        query = """
        MERGE (u:User {id:$user_id})

        MERGE (m:Medication {name:$medication})

        MERGE (u)-[:TAKES_MEDICATION]->(m)
        """

        session.run(
            query,
            user_id=user_id,
            medication=medication
        )