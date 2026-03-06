def detectIntent(message: str):

    message = message.lower()

    # question indicators
    question_words = [
        "what",
        "when",
        "how",
        "did",
        "which",
        "show",
        "list",
        "do i",
        "did i",
        "have i",
        "when did"
    ]

    # ingestion indicators
    health_verbs = [
        "had",
        "have",
        "having",
        "got",
        "felt",
        "feeling",
        "suffered",
        "took",
        "taking"
    ]

    # Check for retrieval
    if "?" in message:
        return "retrieval"

    for word in question_words:
        if message.startswith(word):
            return "retrieval"

    # Check for ingestion
    for verb in health_verbs:
        if verb in message:
            return "ingestion"

    # fallback
    return "ingestion"