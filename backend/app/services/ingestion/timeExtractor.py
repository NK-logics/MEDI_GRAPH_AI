from datetime import datetime, timedelta


def extract_time_from_text(message: str):

    message = message.lower()

    today = datetime.today().date()

    if "today" in message:
        return today

    if "yesterday" in message:
        return today - timedelta(days=1)

    if "last night" in message:
        return today - timedelta(days=1)

    if "last week" in message:
        return today - timedelta(days=7)

    return today