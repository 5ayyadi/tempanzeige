from datetime import timedelta, datetime, date

def time_to_date(offer_date: str) -> str:
    """Converts given offer_date to date object."""
    if "." in offer_date:
        return datetime.strptime(offer_date, "%d.%m.%Y").date().isoformat()
    elif "Heute" in offer_date:
        return date.today().isoformat()
    elif "Gestern" in offer_date:
        return (date.today() - timedelta(days=1)).isoformat()
    else:
        raise ValueError("Unsupported time format")
