from .entityDictionary import SYMPTOM_MAP, TRIGGER_MAP, MEDICATION_MAP

def normalizeSymptoms(rawSymptoms):
    
    normalized = []

    for symptom in rawSymptoms:
        
        symptom = symptom.lower()

        for canonical, variants in SYMPTOM_MAP.items():

            if symptom in variants:
                normalized.append(canonical)
    
    return list(set(normalized))

def normalizeTriggers(rawTriggers):

    normalized = []

    for trigger in rawTriggers:

        trigger = trigger.lower()

        for canonical, variants in TRIGGER_MAP.items():

            if trigger in variants:

                normalized.append(canonical)
    
    return list(set(normalized))

def normalizeMedication(rawMedications):

    normalized = []

    for med in rawMedications:
        
        med = med.lower()

        for canonical, variants in MEDICATION_MAP.items():

            if med in variants:

                normalized.append(canonical)

    return list(set(normalized))

def normalizeEntities(rawEntities):

    normalized = {}

    normalized["symptoms"] = normalizeSymptoms(rawEntities["symptoms"])

    normalized["triggers"] = normalizeTriggers(rawEntities["triggers"])

    normalized["medications"] = normalizeMedication(rawEntities["medications"])

    return normalized