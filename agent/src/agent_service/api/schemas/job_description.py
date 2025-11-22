from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class KeywordWeightSchema(BaseModel):
    """Schema for weighted keyword"""
    text: str
    weight: float = Field(ge=0.0, le=1.0, description="Weight from 0 to 1")
    category: str = Field(description="Category: required, preferred, nice_to_have")


class JobDescriptionSchema(BaseModel):
    """Schema for analyzed job description"""
    id: Optional[str] = None
    raw_text: str
    company: Optional[str] = None
    position: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    responsibilities: List[str] = []
    qualifications: List[str] = []
    industry: Optional[str] = None
    keywords: List[KeywordWeightSchema] = []
    analyzed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "raw_text": "We are looking for a Senior Backend Engineer...",
                "company": "Acme Corp",
                "position": "Senior Backend Engineer",
                "required_skills": ["Python", "PostgreSQL", "Kubernetes"],
                "preferred_skills": ["Go", "Redis", "AWS"],
                "keywords": [
                    {
                        "text": "microservices",
                        "weight": 0.9,
                        "category": "required"
                    },
                    {
                        "text": "scalability",
                        "weight": 0.8,
                        "category": "required"
                    }
                ]
            }
        }


class AnalyzeJDRequest(BaseModel):
    """Request to analyze job description"""
    raw_text: str = Field(..., min_length=50, description="Job description text (minimum 50 characters)")

    class Config:
        json_schema_extra = {
            "example": {
                "raw_text": """
                Senior Backend Engineer - Acme Corp

                We are seeking a talented Senior Backend Engineer to join our team.

                Requirements:
                - 5+ years of experience in backend development
                - Strong proficiency in Python and Go
                - Experience with microservices architecture
                - Expertise in PostgreSQL and Redis
                - Kubernetes and Docker experience
                - Strong problem-solving skills

                Responsibilities:
                - Design and implement scalable backend systems
                - Lead technical discussions and architecture decisions
                - Mentor junior engineers
                - Collaborate with cross-functional teams
                """
            }
        }


class AnalyzeJDResponse(BaseModel):
    """Response from JD analysis"""
    success: bool
    job_description: Optional[JobDescriptionSchema] = None
    error: Optional[str] = None
