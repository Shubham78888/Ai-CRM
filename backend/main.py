from fastapi import FastAPI
from pydantic import BaseModel
from agent.graph import run_agent
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import time

from database import init_db

app = FastAPI(
    title="AI CRM Assistant API",
    version="1.0.0",
    description="AI-First CRM HCP Module with LangGraph Agent"
)

class ChatRequest(BaseModel):
    text: str
    current_data: dict = {}

class ChatResponse(BaseModel):
    response: Dict[str, Any]
    thinking_time: float
    message: str
    status: str = "success"

@app.post("/ai/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Process user input through LangGraph agent and return AI response
    
    This endpoint:
    1. Routes user input intelligently based on intent
    2. Executes appropriate LangGraph tool/node
    3. Persists data to database
    4. Returns structured response with metadata
    """
    start_time = time.time()
    
    try:
        result = run_agent(req.text, req.current_data)
        thinking_time = time.time() - start_time
        
        return ChatResponse(
            response=result,
            thinking_time=thinking_time,
            message="AI analysis completed successfully",
            status="success"
        )
    except Exception as e:
        thinking_time = time.time() - start_time
        return ChatResponse(
            response={"error": str(e)},
            thinking_time=thinking_time,
            message=f"Error processing request: {str(e)}",
            status="error"
        )

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "AI CRM Assistant",
        "version": "1.0.0",
        "agent": "LangGraph-powered"
    }

@app.get("/")
def root():
    """Welcome endpoint"""
    return {
        "message": "AI CRM HCP Module API",
        "endpoints": {
            "chat": "POST /ai/chat",
            "health": "GET /health"
        },
        "agent": "LangGraph with 5 tools"
    }

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
init_db()