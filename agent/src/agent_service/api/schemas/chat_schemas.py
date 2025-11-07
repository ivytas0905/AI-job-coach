"""Pydantic schemas for Chat Assistant API"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


# Request Schemas

class ChatMessageRequest(BaseModel):
    """Request to send chat message"""
    resume_version_id: str = Field(..., description="Resume version ID for context")
    message: str = Field(..., min_length=1, description="User's message")
    chat_session_id: Optional[str] = Field(None, description="Existing chat session ID (or null for new session)")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "resume_version_id": "version-123",
                "message": "How can I improve my Python experience bullet points?",
                "chat_session_id": None
            }]
        }
    }


# Response Schemas

class RelevantContext(BaseModel):
    """Relevant resume context retrieved"""
    content: str
    company: str
    score: float = Field(..., description="Relevance score (0.0 to 1.0)")


class ChatMessageResponse(BaseModel):
    """Response for chat message"""
    session_id: str = Field(..., description="Chat session ID")
    reply: str = Field(..., description="AI assistant's reply")
    relevant_context: List[RelevantContext] = Field(..., description="Relevant resume experiences used for context")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "session_id": "session-456",
                "reply": "To improve your Python experience bullet points, I recommend...",
                "relevant_context": [
                    {
                        "content": "Developed Python-based data pipeline...",
                        "company": "Tech Corp",
                        "score": 0.89
                    }
                ]
            }]
        }
    }


class ChatHistoryResponse(BaseModel):
    """Response for chat history"""
    session_id: str
    messages: List[Dict[str, Any]]
    created_at: str
    last_activity: str
