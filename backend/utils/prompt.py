import json
from utils.llm import llm

def build_prompt(user_input, current_data={}):
    return f"""
You are a CRM assistant for pharmaceutical sales reps.
You are editing a CRM record.

Current Data:
{json.dumps(current_data)}

User Update:
{user_input}

STRICT RULES:
- interaction_type must be either "visit" or "call"
- interaction_date must be in YYYY-MM-DD format
- If doctor shows interest → "positive"
- If neutral / no clear emotion → "neutral"
- If doctor rejects / not interested / unhappy → "negative"
- if any field is missing, return an empty string "" instead of null
- products_discussed must always be an array
- Do NOT guess dates
- If date is not explicitly mentioned, return ""
- Do NOT convert "today", "aaj", etc into actual date
- Only update mentioned fields
- Keep all other fields unchanged
- Return FULL JSON (all fields present)
- Always capitalize first letter of sentences.
- Use professional tone (e.g., "Doctor was happy" instead of "he was happy").
- Do not use informal words like "he", "she", use "Doctor".
- Keep summaries concise and clear.


Return ONLY valid JSON.

Fields:
- hcp_name
- interaction_type
- interaction_date
- products_discussed
- discussion_summary
- doctor_feedback
- follow_up_action
- sentiment

Text:
{user_input}
"""
