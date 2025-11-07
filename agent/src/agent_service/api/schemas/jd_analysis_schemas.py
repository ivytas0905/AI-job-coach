"""Pydantic schemas for JD Analysis API"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Request Schemas

class AnalyzeJDRequest(BaseModel):
    """Request for JD analysis"""
    jd_text: str = Field(..., min_length=50, description="Job description text (minimum 50 characters)")
    job_title: str = Field(..., min_length=2, description="Job title")
    company: Optional[str] = Field(None, description="Company name (optional)")
    job_url: Optional[str] = Field(None, description="URL to job posting (optional)")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "jd_text": "We are seeking a Senior Machine Learning Engineer...",
                "job_title": "Senior Machine Learning Engineer",
                "company": "Tech Corp",
                "job_url": "https://example.com/jobs/123"
            }]
        }
    }


# Response Schemas

class KeywordItem(BaseModel):
    """Individual keyword with metadata"""
    keyword: str
    weight: float = Field(..., ge=0.0, le=1.0, description="Importance weight (0.0 to 1.0)")
    type: str = Field(..., description="Keyword type: technical_skill, soft_skill, tool, certification, domain_knowledge")


class JDAnalysisResponse(BaseModel):
    """Response for JD analysis"""
    jd_id: str = Field(..., description="Unique ID for this analysis")
    top_keywords: List[KeywordItem] = Field(..., description="TOP 20 keywords sorted by importance")
    required_skills: List[str] = Field(default_factory=list, description="Required skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred/nice-to-have skills")
    common_verbs: List[str] = Field(default_factory=list, description="Common action verbs")
    common_nouns: List[str] = Field(default_factory=list, description="Common domain nouns")
    industry: str = Field(..., description="Industry/domain classification")
    cached: bool = Field(False, description="Whether result was retrieved from cache")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "jd_id": "550e8400-e29b-41d4-a716-446655440000",
                "top_keywords": [
                    {"keyword": "Python", "weight": 0.95, "type": "technical_skill"},
                    {"keyword": "Machine Learning", "weight": 0.90, "type": "technical_skill"}
                ],
                "required_skills": ["Python", "ML", "TensorFlow"],
                "preferred_skills": ["AWS", "Docker"],
                "common_verbs": ["develop", "implement", "optimize"],
                "common_nouns": ["system", "model", "pipeline"],
                "industry": "technology",
                "cached": False
            }]
        }
    }


class JDAnalysisHistoryItem(BaseModel):
    """Single item in JD analysis history"""
    jd_id: str
    company: Optional[str]
    job_title: str
    analyzed_at: str  # ISO format datetime
    keyword_count: int


class JDAnalysisHistoryResponse(BaseModel):
    """Response for user's JD analysis history"""
    analyses: List[JDAnalysisHistoryItem]
    total: int
