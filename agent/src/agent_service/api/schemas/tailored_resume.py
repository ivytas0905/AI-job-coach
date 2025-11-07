from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class BulletOptimizationSchema(BaseModel):
    """Schema for bullet point optimization"""
    bullet_id: str
    original_text: str
    optimized_text: str
    improvements: List[str] = []
    keyword_matches: List[str] = []
    status: str = Field(default="pending", description="pending, accepted, rejected")

    class Config:
        json_schema_extra = {
            "example": {
                "bullet_id": "bullet-123",
                "original_text": "Led team to improve system performance",
                "optimized_text": "Spearheaded team of 5 engineers to optimize system performance by 300%, reducing latency from 2s to 0.5s",
                "improvements": [
                    "Added quantifiable metrics (300%, 2s→0.5s)",
                    "Stronger action verb (Spearheaded vs Led)",
                    "Added team size context (5 engineers)"
                ],
                "keyword_matches": ["optimize", "performance", "latency"],
                "status": "pending"
            }
        }


class TailoredResumeSchema(BaseModel):
    """Schema for tailored resume"""
    id: Optional[str] = None
    master_resume_id: str
    jd_id: str
    selected_experience_ids: List[str] = []
    selected_bullet_optimizations: List[BulletOptimizationSchema] = []
    selected_education_ids: List[str] = []
    selected_skills: List[str] = []
    match_score: float = Field(ge=0.0, le=100.0)
    ats_score: float = Field(ge=0.0, le=100.0)
    created_at: Optional[datetime] = None


class TailorResumeRequest(BaseModel):
    """Request to create tailored resume"""
    master_resume_id: str
    jd_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "master_resume_id": "master-resume-123",
                "jd_id": "jd-456"
            }
        }


class TailorResumeResponse(BaseModel):
    """Response from tailoring resume"""
    success: bool
    tailored_resume: Optional[TailoredResumeSchema] = None
    error: Optional[str] = None


class UpdateBulletStatusRequest(BaseModel):
    """Request to update bullet optimization status"""
    bullet_id: str
    status: str = Field(description="accepted or rejected")

    class Config:
        json_schema_extra = {
            "example": {
                "bullet_id": "bullet-123",
                "status": "accepted"
            }
        }


class ApplyOptimizationsRequest(BaseModel):
    """Request to apply selected optimizations"""
    tailored_resume_id: str
    accepted_bullet_ids: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "tailored_resume_id": "tailored-123",
                "accepted_bullet_ids": ["bullet-1", "bullet-3", "bullet-5"]
            }
        }
