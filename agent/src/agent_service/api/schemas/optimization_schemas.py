"""Pydantic schemas for Resume Optimization API"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


# Request Schemas

class OptimizeResumeRequest(BaseModel):
    """Request for resume optimization"""
    resume_data: Dict[str, Any] = Field(..., description="Parsed resume data structure")
    target_keywords: List[str] = Field(..., description="Target keywords from JD analysis")
    job_title: str = Field(..., description="Target job title")
    resume_version_id: Optional[str] = Field(None, description="Resume version ID for tracking")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "resume_data": {
                    "experience": [
                        {
                            "company": "Tech Corp",
                            "title": "Software Engineer",
                            "bullet_points": [
                                "Developed web applications",
                                "Worked with team members"
                            ]
                        }
                    ]
                },
                "target_keywords": ["Python", "Machine Learning", "TensorFlow"],
                "job_title": "Senior ML Engineer",
                "resume_version_id": "version-123"
            }]
        }
    }


# Response Schemas

class Hint(BaseModel):
    """Hint for user to improve their resume bullet"""
    type: str = Field(..., description="Type of hint (quantification, technology, etc.)")
    message: str = Field(..., description="Hint message to display")
    follow_up_question: Optional[str] = Field(None, description="Follow-up question to ask user")
    placeholder: Optional[str] = Field(None, description="Placeholder text for missing information")


class OptimizationSuggestion(BaseModel):
    """Single optimization suggestion"""
    section: str = Field(..., description="Resume section (experience, skills, summary)")
    subsection: str = Field(..., description="Subsection identifier (e.g., company name or job title)")
    original_text: str = Field(..., description="Original text")
    optimized_text: str = Field(..., description="Optimized text")
    improvements: List[str] = Field(..., description="List of improvements made")
    score_improvement: float = Field(..., description="Estimated score improvement")
    keywords_added: List[str] = Field(default_factory=list, description="Keywords added in optimization")
    hints: List[Hint] = Field(default_factory=list, description="Hints for further improvement")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "section": "experience",
                "subsection": "Tech Corp - Software Engineer",
                "original_text": "Developed web applications",
                "optimized_text": "Architected and deployed 3 high-traffic web applications using Python and Django, improving page load time by 40% and serving 100K+ daily users",
                "improvements": ["Applied STAR framework", "Added quantification", "Added keywords: Python"],
                "score_improvement": 45.0,
                "keywords_added": ["Python", "Django"]
            }]
        }
    }


class OptimizeResumeResponse(BaseModel):
    """Response for resume optimization"""
    optimizations: List[OptimizationSuggestion]
    total_suggestions: int
    estimated_score_improvement: float


class AcceptOptimizationRequest(BaseModel):
    """Request to accept/reject optimization suggestion"""
    optimization_id: str
    action: str = Field(..., pattern="^(accepted|rejected|modified)$")
    modified_text: Optional[str] = None
