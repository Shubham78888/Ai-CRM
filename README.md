# AI-First CRM HCP Module

An advanced Healthcare Professional (HCP) interaction management system powered by AI, LangGraph, and LLMs. Designed for pharmaceutical sales representatives to log, analyze, and manage interactions with healthcare professionals.

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Core Features](#core-features)
- [LangGraph Agent & Tools](#langgraph-agent--tools)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)

---

## 🎯 Overview

**Task**: Design an AI-First CRM system with a "Log Interaction Screen" that allows users to log HCP interactions via structured form or conversational chat interface.

**Key Requirement**: Utilize LangGraph for intelligent agent workflow management with minimum 5 specialized tools.

**Live Demo**: 
- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`

---

## 🏗️ Architecture

The system follows a **microservices architecture** with clear separation between frontend and backend:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────────┐         ┌──────────────────────────┐   │
│  │  Form Panel  │         │   Chat Panel (AI)        │   │
│  └──────────────┘         └──────────────────────────┘   │
│         │                            │                    │
│         └────────────────┬───────────┘                    │
│                          │                                │
└──────────────────────────┼────────────────────────────────┘
                           │
                    API Gateway
                    (Axios/Fetch)
                           │
┌──────────────────────────┼────────────────────────────────┐
│              Backend (FastAPI + LangGraph)                │
│         ┌────────────────▼───────────────┐                │
│         │   FastAPI Server (Port 8000)   │                │
│         └────────────┬───────────────────┘                │
│                      │                                    │
│         ┌────────────▼───────────────┐                    │
│         │   LangGraph Agent          │                    │
│         │  (StateGraph Router)       │                    │
│         └────────────┬───────────────┘                    │
│                      │                                    │
│    ┌─────────────────┼─────────────────┐                  │
│    │                 │                 │                  │
│ ┌──▼──┐  ┌─────────▼───┐  ┌────────▼─┐ │  ┌────────────┐ │
│ │Tool1│  │ Tool2 Tool3 │  │ Tool4   │ │  │ Tool5      │ │
│ │Log  │  │ Edit Summary│  │ Suggest │ │  │ Fetch      │ │
│ └──┬──┘  └──┬──────┬───┘  │ Follow  │ │  │ History    │ │
│    │        │      │      └────┬────┘ │  └────────────┘ │
│    │        │      │           │      │                  │
│    └────────┼──────┼───────────┼──────┘                  │
│             │      │           │                         │
│    ┌────────▼──────▼───────────▼────────┐                │
│    │   LLM (Groq - gemma2-9b-it)        │                │
│    └────────┬───────────────────────────┘                │
│             │                                            │
│    ┌────────▼───────────────┐                            │
│    │  Database Layer        │                            │
│    │  (SQLAlchemy ORM)      │                            │
│    └────────┬───────────────┘                            │
│             │                                            │
│    ┌────────▼───────────────┐                            │
│    │  Database              │                            │
│    │ (MySQL/PostgreSQL)     │                            │
│    └───────────────────────┘                             │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19.2.5
- **State Management**: Redux & Redux Toolkit
- **Styling**: Tailwind CSS 4.2.4
- **Build Tool**: Vite 8.0.10
- **Font**: Google Inter (all weights 100-900)

### Backend
- **Framework**: FastAPI (Python)
- **Agent Framework**: **LangGraph** (StateGraph for routing)
- **LLM**: Groq (gemma2-9b-it model)
- **ORM**: SQLAlchemy
- **Database**: MySQL/PostgreSQL (SQLite for dev)

### Infrastructure
- **API Communication**: REST with CORS enabled
- **Async Support**: FastAPI async/await
- **Database Abstraction**: SQLAlchemy SessionLocal

---

## ✨ Core Features

### 1. **Dual Interface**
- **Form Panel**: Structured data entry with validation
- **Chat Panel**: Natural language conversation with AI

### 2. **Real-time Data Sync**
- Redux state synchronization between components
- Form data passes to AI for context-aware responses
- Chat messages update form automatically

### 3. **AI-Powered Analysis**
- Entity extraction from natural language
- Sentiment analysis on interactions
- Automatic action item identification
- Contextual follow-up suggestions

### 4. **Database Persistence**
- All interactions saved to database
- Historical data retrieval
- Data relationships and dependencies maintained
- Automatic timestamps on all records

---

## 🤖 LangGraph Agent & Tools

### Agent Overview

The LangGraph agent uses a **StateGraph** architecture to intelligently route user requests to appropriate tools based on intent. The agent maintains state across the entire workflow and ensures consistent data flow.

### State Machine Flow

```
START
  │
  ▼
┌─────────────────┐
│  Router Node    │  ◄─── Analyzes user intent
└────────┬────────┘      ◄─── Keywords: edit, suggest, summary, history
         │
    ┌────┴──────────────────────────┐
    │                               │
    ▼                               ▼
┌─────────┐                    ┌──────────┐
│ log_tool│                    │edit_tool │  
└────┬────┘                    └──────┬───┘
     │        ┌─────────────┐         │
     ├───────►│summary_tool │◄────────┤
     │        └─────────────┘         │
     │        ┌─────────────┐         │
     └───────►│suggest_tool │◄────────┘
              └─────────────┘
              ┌─────────────┐
              │history_tool │
              └─────────────┘
              
    All paths converge to END
```

### 5 Core Tools

#### **1. Log Interaction Tool** ✍️
**Purpose**: Capture new HCP interaction data using AI
**Input**: Natural language description of the interaction
**Process**:
- LLM extracts structured JSON from user text
- Entity recognition for HCP names, products, dates
- Sentiment analysis on discussion tone
- Action items extraction
- Database persistence

**Output**:
```json
{
  "hcp_name": "Dr. Sharma",
  "interaction_type": "visit",
  "interaction_date": "2026-04-24",
  "products_discussed": ["Aspirin", "Paracetamol"],
  "discussion_summary": "Doctor expressed interest in new formulation",
  "doctor_feedback": "Positive response to product benefits",
  "sentiment": "positive",
  "action_items": ["Send product literature", "Schedule follow-up"],
  "db_id": 1,
  "db_status": "saved"
}
```

#### **2. Edit Interaction Tool** ✏️
**Purpose**: Modify existing logged interactions
**Input**: Current data + natural language update description
**Process**:
- Merges new updates with existing data
- Validates data consistency
- Preserves unchanged fields
- Updates database record
- Maintains audit trail with timestamps

**Output**: Updated interaction record with confirmation

#### **3. Suggest Follow-up Tool** 💡
**Purpose**: Generate AI-powered follow-up recommendations
**Input**: Interaction context + HCP name
**Process**:
- Analyzes interaction content for sales opportunities
- Considers doctor sentiment and feedback
- Generates contextual follow-up strategy
- Prioritizes by business impact

**Output**:
```json
{
  "follow_up_action": "Schedule video call to discuss formulation details and address doctor's concerns about shelf-life",
  "recommended_by": "AI Agent",
  "timestamp": "2026-04-24T15:30:00"
}
```

#### **4. Summarize Interaction Tool** 📝
**Purpose**: Extract key discussion points and insights
**Input**: Full interaction description + products discussed
**Process**:
- Uses LLM for abstractive summarization
- Focuses on key business points
- Maintains context and importance
- Limit to 1-2 meaningful sentences

**Output**:
```json
{
  "discussion_summary": "Doctor appreciated new aspirin formulation efficacy and requested samples for patient trials",
  "summary_type": "AI Generated",
  "timestamp": "2026-04-24T15:30:00"
}
```

#### **5. Fetch History Tool** 📚
**Purpose**: Retrieve historical interactions with specific HCP
**Input**: HCP name
**Process**:
- Queries database for all interactions
- Sorts by most recent
- Aggregates interaction patterns
- Calculates interaction frequency

**Output**:
```json
{
  "hcp_name": "Dr. Sharma",
  "total_interactions": 5,
  "history": [
    {
      "id": 1,
      "date": "2026-04-24",
      "type": "visit",
      "summary": "Positive response to new formulation",
      "created_at": "2026-04-24T15:30:00"
    }
  ],
  "status": "success"
}
```

### Agent Routing Logic

```python
if "edit" in user_input.lower():
    route = "edit_tool"
elif "suggest" in user_input.lower() or "follow" in user_input.lower():
    route = "suggest_tool"
elif "summary" in user_input.lower():
    route = "summarize_tool"
elif "history" in user_input.lower():
    route = "history_tool"
else:
    route = "log_tool"  # Default
```

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn
- MySQL 8.0+ or PostgreSQL 12+ (optional, uses SQLite by default)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic langchain langchain-groq langgraph sqlalchemy python-dotenv

# Create .env file
cat > .env << EOF
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///./crm.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/crm_db
# DB module pip install PyMySQL
# Datautils pip install python-dateutil

EOF

# Initialize database (create tables)
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"

# Run backend server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd ..

# Install dependencies
npm install

# Create .env file (if needed)
# VITE_API_URL=http://localhost:8000

# Run development server
npm run dev

# Backend will be available at http://localhost:5173
```

---

## 🚀 Usage

### 1. **Via Chat Panel (Natural Language)**

User Input:
```
"Today I visited Dr. Patel. We discussed Aspirin and Paracetamol. 
He was very interested in the new formulation and wants samples."
```

Agent Flow:
1. Router detects no keywords → Routes to `log_tool`
2. LLM extracts structured data
3. Database saves interaction
4. AI generates sentiment & action items
5. Response displayed in chat

### 2. **Via Form Panel (Structured Entry)**

1. Fill form fields manually
2. Send to chat
3. AI validates and enhances data
4. Saves to database

### 3. **Editing Past Interactions**

User Input:
```
"Edit: Change the sentiment to negative because the doctor had concerns"
```

Agent Flow:
1. Router detects "edit" → Routes to `edit_tool`
2. Current data merged with updates
3. Database record updated
4. Confirmation returned

### 4. **Getting Follow-up Suggestions**

User Input:
```
"Suggest next steps for Dr. Sharma"
```

Agent Flow:
1. Router detects "suggest" → Routes to `suggest_tool`
2. LLM analyzes interaction context
3. Generates contextual recommendation
4. Returned to user

### 5. **Viewing History**

User Input:
```
"Show me history with Dr. Sharma"
```

Agent Flow:
1. Router detects "history" → Routes to `history_tool`
2. Queries database for all interactions
3. Returns timeline and patterns
4. Displays in chat

---

## 📡 API Documentation

### Health Check
```http
GET /health
```

**Response**:
```json
{
  "status": "ok",
  "service": "AI CRM Assistant",
  "version": "1.0.0",
  "agent": "LangGraph-powered"
}
```

### AI Chat Endpoint
```http
POST /ai/chat
Content-Type: application/json

{
  "text": "I visited Dr. Sharma today and discussed Aspirin products",
  "current_data": {
    "hcp_name": "Dr. Sharma",
    "products_discussed": ["Aspirin"]
  }
}
```

**Response**:
```json
{
  "response": {
    "hcp_name": "Dr. Sharma",
    "interaction_type": "visit",
    "interaction_date": "2026-04-24",
    "products_discussed": ["Aspirin"],
    "discussion_summary": "...",
    "sentiment": "positive",
    "db_id": 1,
    "db_status": "saved",
    "agent_metadata": {
      "route": "log",
      "timestamp": "2026-04-24T15:30:00",
      "interaction_id": 1,
      "errors": []
    }
  },
  "thinking_time": 2.34,
  "message": "AI analysis completed successfully",
  "status": "success"
}
```

---

## 💾 Database Schema

### HCPInteraction Model

```python
class HCPInteraction(Base):
    __tablename__ = "hcp_interactions"
    
    id: Integer (Primary Key)
    hcp_name: String(255) - Healthcare professional name
    interaction_type: String(50) - visit, call, email, meeting
    interaction_date: String(50) - YYYY-MM-DD format
    products_discussed: JSON - Array of product names
    discussion_summary: Text - AI-generated summary
    doctor_feedback: Text - Doctor's comments
    follow_up_action: Text - Suggested next steps
    sentiment: String(50) - positive, neutral, negative
    key_points: JSON - Extracted key discussion points
    action_items: JSON - Generated action items
    created_at: DateTime - Timestamp of record creation
```

---

## 📁 Project Structure

```
ai-crm-frontend/
├── backend/
│   ├── agent/
│   │   ├── graph.py          # LangGraph StateGraph implementation
│   │   └── tools.py          # 5 core tools with DB persistence
│   ├── utils/
│   │   ├── llm.py            # Groq gemma2-9b-it configuration
│   │   ├── prompt.py         # Prompt templates
│   │   ├── date_parser.py    # Date parsing utilities
│   │   ├── validator.py      # Data validation & cleaning
│   │   └── requirements.txt  # Python dependencies
│   ├── database.py           # SQLAlchemy models & config
│   ├── main.py               # FastAPI application
│   └── .env.example          # Environment variables template
│
├── src/
│   ├── components/
│   │   ├── ChatPanel.jsx     # AI conversation interface
│   │   └── FormPanel.jsx     # Structured data entry form
│   ├── pages/
│   │   └── Dashboard.jsx     # Main layout page
│   ├── redux/
│   │   ├── store.js          # Redux store configuration
│   │   └── formSlice.js      # Form state management
│   ├── services/
│   │   └── apiService.js     # Backend API communication
│   ├── hooks/
│   │   └── useChatPanel.js   # Custom chat hooks
│   ├── App.jsx               # Root component
│   ├── main.jsx              # React entry point
│   ├── App.css               # Styling
│   └── index.css             # Global styles with Inter font
│
├── public/                    # Static assets
├── package.json              # NPM dependencies
├── vite.config.js            # Vite configuration
├── index.html                # HTML entry with Google Inter
├── .env.example              # Environment template
├── README.md                 # This file
└── ARCHITECTURE.md           # Detailed architecture docs
```

---

## 🎓 Learning Outcomes

This project demonstrates:

✅ **LangGraph Agent Framework**: State machines, routing, tool orchestration
✅ **LLM Integration**: Groq API, prompt engineering, structured output extraction
✅ **Full-Stack Development**: React + FastAPI integration
✅ **Database Design**: SQLAlchemy ORM, data persistence
✅ **AI/ML Concepts**: Entity extraction, sentiment analysis, text summarization
✅ **Software Architecture**: Microservices, separation of concerns, API design
✅ **Frontend Optimization**: Redux state management, component reusability

---

## 📹 Video Demonstration Guide

For the submission video (10-15 minutes), cover:

1. **Frontend Walkthrough (3-4 min)**
   - Show both Chat and Form panels
   - Demonstrate dual input methods
   - Show real-time data sync between components

2. **Tool Demonstrations (5-7 min)**
   - **Tool 1**: Log interaction via chat → Show saved to database
   - **Tool 2**: Edit interaction → Show update reflected
   - **Tool 3**: Get follow-up suggestion → Show contextual AI response
   - **Tool 4**: Summarize interaction → Show key points extraction
   - **Tool 5**: Fetch history → Show database query results

3. **Code Flow Explanation (2-3 min)**
   - Show LangGraph StateGraph architecture
   - Explain routing logic
   - Demonstrate database persistence
   - Show API request/response cycle

4. **Personal Learning (1-2 min)**
   - Key insights from implementing LangGraph
   - Challenges overcome
   - Future enhancements

---

## 🔧 Configuration

### Environment Variables

Create `.env` in backend directory:

```bash
# Groq API Configuration
GROQ_API_KEY=gsk_xxxxx...

# Database Configuration
DATABASE_URL=sqlite:///./crm.db
# Or PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost:5432/crm_db

# API Configuration (optional)
API_PORT=8000
API_HOST=0.0.0.0
```

---

## 📝 License

This project is part of an educational assignment and follows academic integrity standards.

---

## 👨‍💻 Author

AI-First CRM HCP Module - Assignment Round 1

**Submitted**: April 24, 2026

---

## 📞 Support & Contact

For issues or questions:
1. Check the ARCHITECTURE.md for detailed system design
2. Review the video demonstration for usage examples
3. Examine the code comments for implementation details

---

**Status**: ✅ Production Ready - All 5 LangGraph Tools Implemented with Database Persistence
