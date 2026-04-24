"""Validation utilities for CRM data"""
import json
import re
from datetime import datetime

def extract_json(text):
    """Extract and validate JSON from text"""
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return data
    except Exception as e:
        print(f"JSON extraction error: {e}")
    return {}

def validate_date(date_str):
    """Validate date format YYYY-MM-DD"""
    if not date_str:
        return ""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except:
        return ""

def validate_interaction_type(itype):
    """Validate interaction type"""
    valid = ["visit", "call", "email", "meeting"]
    return itype.lower() if itype and itype.lower() in valid else ""

def validate_sentiment(sentiment):
    """Validate sentiment value"""
    valid = ["positive", "neutral", "negative"]
    return sentiment.lower() if sentiment and sentiment.lower() in valid else ""

def clean_interaction_data(data):
    """Clean and validate interaction data"""
    cleaned = {
        "hcp_name": str(data.get("hcp_name", "")).strip(),
        "interaction_type": validate_interaction_type(data.get("interaction_type", "")),
        "interaction_date": validate_date(data.get("interaction_date", "")),
        "products_discussed": data.get("products_discussed", []) if isinstance(data.get("products_discussed"), list) else [],
        "discussion_summary": str(data.get("discussion_summary", "")).strip(),
        "doctor_feedback": str(data.get("doctor_feedback", "")).strip(),
        "follow_up_action": str(data.get("follow_up_action", "")).strip(),
        "sentiment": validate_sentiment(data.get("sentiment", "")),
        "key_points": data.get("key_points", []) if isinstance(data.get("key_points"), list) else [],
        "action_items": data.get("action_items", []) if isinstance(data.get("action_items"), list) else []
    }
    return cleaned
