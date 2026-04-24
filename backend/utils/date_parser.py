from datetime import datetime, timedelta
from dateutil import parser

def extract_date(user_input, existing_date=""):
    text = user_input.lower()

    today = datetime.today()

    # ✅ TODAY
    if "today" in text or "aaj" in text:
        return today.strftime("%Y-%m-%d")

    # ✅ YESTERDAY
    if "yesterday" in text or "kal" in text:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # ✅ LAST WEEK
    if "last week" in text:
        return (today - timedelta(days=7)).strftime("%Y-%m-%d")

    # ✅ TRY PARSING REAL DATE
    try:
        parsed = parser.parse(text, fuzzy=True)
        return parsed.strftime("%Y-%m-%d")
    except:
        pass

    # ✅ FALLBACK (keep existing)
    return existing_date or ""