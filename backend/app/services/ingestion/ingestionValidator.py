def validate_entities(entities: dict):

    "Validates extracted entities before graph insertion"

    symptoms = entities.get("symptoms", [])
    triggers = entities.get("triggers", [])
    medications = entities.get("medications", [])

    if not symptoms and not triggers and not medications:
        return False

    return True