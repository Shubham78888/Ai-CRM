import json
import re
from utils.prompt import build_prompt
from utils.llm import llm
from utils.validator import extract_json, clean_interaction_data
from datetime import datetime, timedelta
from utils.date_parser import extract_date
from database import SessionLocal, HCPInteraction


# ==================== DATABASE OPERATIONS ====================

def save_interaction(data):
    """Save interaction to database"""
    try:
        session = SessionLocal()
        
        # Clean data
        clean_data = clean_interaction_data(data)
        
        # Create model instance
        interaction = HCPInteraction(
            hcp_name=clean_data["hcp_name"],
            interaction_type=clean_data["interaction_type"],
            interaction_date=clean_data["interaction_date"],
            products_discussed=clean_data["products_discussed"],
            discussion_summary=clean_data["discussion_summary"],
            doctor_feedback=clean_data["doctor_feedback"],
            follow_up_action=clean_data["follow_up_action"],
            sentiment=clean_data["sentiment"],
            key_points=clean_data["key_points"],
            action_items=clean_data["action_items"]
        )
        
        session.add(interaction)
        session.commit()
        
        result = {
            "id": interaction.id,
            "status": "saved",
            "message": f"Interaction with {clean_data['hcp_name']} saved successfully"
        }
        session.close()
        return result
    except Exception as e:
        print(f"Database error: {e}")
        return {"status": "error", "message": str(e)}


def fetch_interaction(interaction_id):
    """Fetch interaction by ID"""
    try:
        session = SessionLocal()
        interaction = session.query(HCPInteraction).filter(
            HCPInteraction.id == interaction_id
        ).first()
        session.close()
        
        if interaction:
            return {
                "id": interaction.id,
                "hcp_name": interaction.hcp_name,
                "interaction_type": interaction.interaction_type,
                "interaction_date": interaction.interaction_date,
                "products_discussed": interaction.products_discussed,
                "discussion_summary": interaction.discussion_summary,
                "doctor_feedback": interaction.doctor_feedback,
                "follow_up_action": interaction.follow_up_action,
                "sentiment": interaction.sentiment,
                "key_points": interaction.key_points,
                "action_items": interaction.action_items,
                "created_at": interaction.created_at.isoformat() if interaction.created_at else None
            }
        return None
    except Exception as e:
        print(f"Database error: {e}")
        return None


def update_interaction(interaction_id, updated_data):
    """Update existing interaction"""
    try:
        session = SessionLocal()
        interaction = session.query(HCPInteraction).filter(
            HCPInteraction.id == interaction_id
        ).first()
        
        if not interaction:
            session.close()
            return {"status": "error", "message": "Interaction not found"}
        
        # Clean and apply updates
        clean_data = clean_interaction_data(updated_data)
        
        for key, value in clean_data.items():
            if hasattr(interaction, key) and value:
                setattr(interaction, key, value)
        
        session.commit()
        session.close()
        
        return {"status": "updated", "message": "Interaction updated successfully"}
    except Exception as e:
        print(f"Database error: {e}")
        return {"status": "error", "message": str(e)}


def fetch_hcp_history(hcp_name):
    """Fetch all interactions for an HCP"""
    try:
        session = SessionLocal()
        interactions = session.query(HCPInteraction).filter(
            HCPInteraction.hcp_name.ilike(f"%{hcp_name}%")
        ).order_by(HCPInteraction.created_at.desc()).all()
        
        session.close()
        
        history = []
        for interaction in interactions:
            history.append({
                "id": interaction.id,
                "date": interaction.interaction_date,
                "type": interaction.interaction_type,
                "summary": interaction.discussion_summary,
                "created_at": interaction.created_at.isoformat() if interaction.created_at else None
            })
        
        return history
    except Exception as e:
        print(f"Database error: {e}")
        return []


# ==================== TOOL IMPLEMENTATIONS ====================

# 1. LOG INTERACTION TOOL
def log_interaction_tool(user_input, current_data=None):
    """
    Log interaction with HCP using AI to extract structured data
    Uses LLM for entity extraction and summarization
    """
    if current_data is None:
        current_data = {}
    
    try:
        # Build prompt for LLM
        prompt = build_prompt(user_input, current_data)
        response = llm.invoke(prompt)
        raw_output = response.content
        
        # Extract JSON from LLM response
        extracted_data = extract_json(raw_output)
        
        # Enrich with date parsing
        enriched_data = enrich_date(extracted_data, user_input)
        
        # Save to database
        db_result = save_interaction(enriched_data)
        
        # Return with DB info
        return {
            **enriched_data,
            "db_id": db_result.get("id"),
            "db_status": db_result.get("status"),
            "db_message": db_result.get("message")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to log interaction: {str(e)}"
        }


# 2. EDIT INTERACTION TOOL
def edit_interaction_tool(user_input, current_data, interaction_id=None):
    """
    Edit existing logged interaction
    Takes user input describing changes and applies them to stored data
    """
    try:
        if not current_data:
            return {"status": "error", "message": "No interaction data provided"}
        
        prompt = f"""
You are editing an existing CRM record.

Current Data:
{json.dumps(current_data)}

User Update:
{user_input}

Return ONLY valid JSON with all fields. Update only mentioned fields and keep others unchanged.
"""
        
        response = llm.invoke(prompt)
        updated_data = extract_json(response.content)
        
        # Merge with current data
        merged = {**current_data, **updated_data}
        enriched = enrich_date(merged, user_input)
        
        # Save to database if interaction_id provided
        if interaction_id:
            db_result = update_interaction(interaction_id, enriched)
            return {
                **enriched,
                "db_status": db_result.get("status"),
                "db_message": db_result.get("message")
            }
        
        return enriched
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to edit interaction: {str(e)}"
        }


# 3. SUGGEST FOLLOW-UP TOOL
def suggest_followup_tool(user_input, hcp_name=""):
    """
    Suggest next follow-up action based on the interaction
    Uses LLM to generate context-aware follow-up recommendations
    """
    try:
        prompt = f"""
You are a pharmaceutical sales CRM assistant. Based on the following interaction, 
suggest the NEXT most important follow-up action.

Interaction Details:
{user_input}

HCP Name: {hcp_name}

Provide a concise, actionable suggestion (1-2 sentences maximum).
Focus on sales strategy and relationship building.

Suggestion:
"""
        response = llm.invoke(prompt)
        suggestion = response.content.strip()
        
        return {
            "follow_up_action": suggestion,
            "recommended_by": "AI Agent",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate follow-up: {str(e)}"
        }


# 4. SUMMARIZE INTERACTION TOOL
def summarize_tool(user_input, products=None):
    """
    Summarize the interaction in key points
    Extracts important discussion points and insights
    """
    try:
        products_context = f"\nProducts Discussed: {', '.join(products)}" if products else ""
        
        prompt = f"""
Summarize this healthcare professional interaction in 1-2 meaningful sentences.
Focus on key discussion points, doctor sentiment, and business impact.

Do NOT return single words or incomplete sentences.

Interaction:
{user_input}
{products_context}

Summary:
"""
        response = llm.invoke(prompt)
        summary = response.content.strip()
        
        return {
            "discussion_summary": summary,
            "summary_type": "AI Generated",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to summarize: {str(e)}"
        }


# 5. FETCH HISTORY TOOL (from database)
def fetch_history_tool(hcp_name):
    """
    Fetch all previous interactions with an HCP from database
    Shows interaction timeline and patterns
    """
    try:
        if not hcp_name:
            return {
                "status": "error",
                "message": "HCP name required"
            }
        
        # Query database
        history = fetch_hcp_history(hcp_name)
        
        return {
            "hcp_name": hcp_name,
            "total_interactions": len(history),
            "history": history,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch history: {str(e)}"
        }


# ==================== HELPER FUNCTIONS ====================

def enrich_date(data, user_input):
    """
    Parse natural language dates and enrich interaction data
    Handles: today, aaj, yesterday, kal, and specific dates
    """
    text = user_input.lower()
    
    if not data.get("interaction_date"):
        if "today" in text or "aaj" in text:
            data["interaction_date"] = datetime.today().strftime("%Y-%m-%d")
        elif "yesterday" in text or "kal" in text:
            data["interaction_date"] = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        # Try to extract date with date_parser utility
        else:
            data["interaction_date"] = extract_date(user_input, "")
    
    return data


def extract_sentiment(interaction_text):
    """
    Extract sentiment from interaction description
    Comprehensive keyword-based analysis with negation handling
    """
    positive_words = [
        "happy", "pleased", "interested", "great", "excellent", "good", 
        "delighted", "satisfied", "impressed", "positive", "enthusiastic",
        "encouraging", "interested in", "keen", "excited", "supportive"
    ]
    negative_words = [
        "unhappy", "concerned", "disappointed", "bad", "poor", "issue",
        "rejected", "refuse", "refused", "not interested", "disinterested",
        "problem", "problems", "difficult", "negative", "objection", 
        "objections", "worried", "hesitant", "reluctant", "critical",
        "unfavorable", "unfavourable", "unsatisfied", "angry", "frustrated",
        "confused", "unclear", "disagree", "concerns", "obstacle"
    ]
    
    text = interaction_text.lower()
    
    # Check for negation patterns ("not interested", "not happy", etc.)
    negation_pattern = r"\b(not|no|don't|doesn't|won't|wouldn't)\s+\w*(interested|happy|pleased|enthusiastic|satisfied|good)"
    has_negation = bool(re.search(negation_pattern, text))
    
    positive_count = sum(1 for word in positive_words if word in text)
    negative_count = sum(1 for word in negative_words if word in text)
    
    # If negation detected with positive words, treat as negative
    if has_negation and positive_count > 0:
        return "negative"
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def extract_action_items(interaction_text):
    """
    Extract action items and follow-ups from interaction text
    Looks for keywords like "need to", "follow up", "send", etc.
    """
    action_patterns = ["send", "follow up", "need to", "must", "schedule", "arrange"]
    items = []
    
    sentences = interaction_text.split(".")
    for sentence in sentences:
        sentence_lower = sentence.lower()
        for pattern in action_patterns:
            if pattern in sentence_lower:
                items.append(sentence.strip())
                break
    
    return items[:5]  # Return top 5 action items