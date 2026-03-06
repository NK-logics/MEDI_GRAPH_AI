from .llm_entityExtractor import extract_entities_llm
from .entityNormalizer import normalizeEntities
from .ingestionValidator import validate_entities
from .graphBuilder import insert_symptoms, insert_triggers, insert_medications
from .timeExtractor import extract_time_from_text


def run_ingestion_pipeline(message: str, user_id: str):

    # Step 1 — LLM extraction
    raw_entities = extract_entities_llm(message)

    # Step 2 — Normalize entities
    normalized_entities = normalizeEntities(raw_entities)

    # Step 3 — Extract time
    reported_date = extract_time_from_text(message)

    # Step 4 — Validate
    is_valid = validate_entities(normalized_entities)

    if not is_valid:
        return {
            "status": "no_data",
            "message": "No health information detected."
        }

    symptoms = normalized_entities["symptoms"]
    triggers = normalized_entities["triggers"]
    medications = normalized_entities["medications"]

    # Step 5 — Insert graph data
    if symptoms:
        insert_symptoms(user_id, symptoms, message, reported_date)

    if triggers:
        insert_triggers(user_id, triggers)

    if medications:
        insert_medications(user_id, medications)

    return {
        "status": "success",
        "stored_entities": normalized_entities,
        "reported_date": str(reported_date)
    }