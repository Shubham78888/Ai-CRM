"""
Database Configuration & Models using SQLAlchemy
Supports MySQL and PostgreSQL
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Database URL Configuration
# MySQL Connection String Format:
# mysql+pymysql://username:password@localhost:3306/crm_db
# Example: mysql+pymysql://root:password@localhost:3306/crm_db

DATABASE_URL = os.getenv("DATABASE_URL")  # MySQL default

# Create Engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Verify connection before using
    connect_args={} if "mysql" in DATABASE_URL else {"check_same_thread": False}
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()


# ==================== MODELS ====================

class HCPInteraction(Base):
    """Model for HCP (Healthcare Professional) Interactions"""
    __tablename__ = "hcp_interactions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    hcp_name = Column(String(255), nullable=False, index=True)
    interaction_type = Column(String(50), nullable=False)  # visit, call, email, meeting
    interaction_date = Column(String(50), nullable=False)
    
    # Interaction Details
    products_discussed = Column(JSON, nullable=True)  # List of products
    discussion_summary = Column(Text, nullable=True)
    doctor_feedback = Column(Text, nullable=True)
    follow_up_action = Column(Text, nullable=True)
    
    # Analysis
    sentiment = Column(String(50), nullable=True)  # positive, neutral, negative
    key_points = Column(JSON, nullable=True)  # Extracted key points
    action_items = Column(JSON, nullable=True)  # Action items from interaction
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255), nullable=True)  # Field rep name
    
    # AI Processing
    ai_confidence = Column(Float, nullable=True)  # Confidence score from LLM
    raw_ai_response = Column(JSON, nullable=True)  # Raw response from LLM

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "hcp_name": self.hcp_name,
            "interaction_type": self.interaction_type,
            "interaction_date": self.interaction_date,
            "products_discussed": self.products_discussed or [],
            "discussion_summary": self.discussion_summary,
            "doctor_feedback": self.doctor_feedback,
            "follow_up_action": self.follow_up_action,
            "sentiment": self.sentiment,
            "key_points": self.key_points or [],
            "action_items": self.action_items or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class HCPProfile(Base):
    """Model for HCP Profiles"""
    __tablename__ = "hcp_profiles"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), unique=True, nullable=False, index=True)
    specialty = Column(String(255), nullable=True)  # Cardiology, Neurology, etc.
    hospital_clinic = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    last_interaction_date = Column(String(50), nullable=True)
    interaction_count = Column(Integer, default=0)
    
    # Preferences
    preferred_contact = Column(String(50), nullable=True)  # call, visit, email
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InteractionHistory(Base):
    """Archive of all interactions for audit trail"""
    __tablename__ = "interaction_history"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, nullable=False, index=True)
    hcp_name = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)  # created, updated, edited
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_by = Column(String(255), nullable=True)


# ==================== DATABASE INITIALIZATION ====================

def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== HELPER FUNCTIONS ====================

def create_interaction(db, interaction_data: dict, created_by: str = None):
    """Create new HCP interaction"""
    interaction = HCPInteraction(
        hcp_name=interaction_data.get("hcp_name"),
        interaction_type=interaction_data.get("interaction_type"),
        interaction_date=interaction_data.get("interaction_date"),
        products_discussed=interaction_data.get("products_discussed"),
        discussion_summary=interaction_data.get("discussion_summary"),
        doctor_feedback=interaction_data.get("doctor_feedback"),
        follow_up_action=interaction_data.get("follow_up_action"),
        sentiment=interaction_data.get("sentiment"),
        key_points=interaction_data.get("key_points"),
        action_items=interaction_data.get("action_items"),
        ai_confidence=interaction_data.get("ai_confidence"),
        raw_ai_response=interaction_data.get("raw_ai_response"),
        created_by=created_by
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def get_interaction(db, interaction_id: int):
    """Get interaction by ID"""
    return db.query(HCPInteraction).filter(HCPInteraction.id == interaction_id).first()


def get_interactions_by_hcp(db, hcp_name: str):
    """Get all interactions for a specific HCP"""
    return db.query(HCPInteraction).filter(HCPInteraction.hcp_name == hcp_name).all()


def update_interaction(db, interaction_id: int, update_data: dict):
    """Update interaction"""
    interaction = get_interaction(db, interaction_id)
    if interaction:
        for key, value in update_data.items():
            if hasattr(interaction, key):
                setattr(interaction, key, value)
        interaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(interaction)
    return interaction


def get_hcp_history(db, hcp_name: str, limit: int = 10):
    """Get recent interactions for an HCP"""
    return db.query(HCPInteraction).filter(
        HCPInteraction.hcp_name == hcp_name
    ).order_by(HCPInteraction.created_at.desc()).limit(limit).all()
