from app.db.neo4j_driver import get_session
from datetime import datetime

def insertSymptoms(userId, symptoms, sourceText):
    
    session = get_session()

    for symptom in symptoms:

        query = """
        MERGE (u:User {id:$user_id})

        MERGE (s:Symptom {name:$symptom})

        MERGE (u)-[:HAS_SYMPTOM {
            reported_at: date(),
            source_text: $source,
            created_at: datetime()
        }]->(s)
        """

        session.run(
            query,
            userId=userId,
            symptom=symptom,
            source=sourceText
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