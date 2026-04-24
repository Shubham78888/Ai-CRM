from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

# Use llama-3.3-70b-versatile as per assignment requirement
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    # temperature=0.7
)