"""
Build Resume request/response schemas
Used by build_resume use case and routes
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional


# ============= Request Schemas =============

class PersonalInfoRequest(BaseModel):
    """Personal information from frontend"""
    fullname: str
    email: EmailStr
    phone: str
    location: Optional[str] = None
    title: Optional[str] = None


class ExperienceRequest(BaseModel):
    """Experience entry from frontend"""
    type: str = "work"  # work, project, volunteer, etc.
    title: str
    company: str
    start_date: str
    end_date: Optional[str] = None
    location: Optional[str] = None
    description: str = ""


class EducationRequest(BaseModel):
    """Education entry from frontend"""
    degree: str
    institution: str
    start_date: str
    end_date: Optional[str] = None
    location: Optional[str] = None


class BuildResumeRequest(BaseModel):
    """
    Complete request schema for building resume
    
    This matches the data structure from frontend
    """
    personal_info: PersonalInfoRequest
    experiences: List[ExperienceRequest]
    education: List[EducationRequest]
    skills: List[str]
    summary: Optional[str] = None
    target_job: Optional[str] = None
    enhance_with_ai: bool = False


# ============= Response Schemas =============

class PersonalInfoResponse(BaseModel):
    """Personal info in response"""
    fullname: str
    email: str
    phone: str
    location: Optional[str] = None
    title: Optional[str] = None


class ExperienceResponse(BaseModel):
    """Experience in response"""
    type: str
    title: str
    company: str
    start_date: str
    end_date: Optional[str] = None
    location: Optional[str] = None
    description: str


class EducationResponse(BaseModel):
    """Education in response"""
    degree: str
    institution: str
    start_date: str
    end_date: Optional[str] = None
    location: Optional[str] = None


class SkillResponse(BaseModel):
    """Skill in response"""
    name: str


class ResumeResponse(BaseModel):
    """Resume data in response"""
    personal_info: PersonalInfoResponse
    experiences: List[ExperienceResponse]
    education: List[EducationResponse]
    skills: List[SkillResponse]
    summary: str
    target_job: Optional[str] = None


class BuildResumeResponse(BaseModel):
    """
    Response schema for build resume endpoint
    """
    success: bool
    resume: ResumeResponse
    preview_html: Optional[str] = None
    message: str = "Resume built successfully"


class ValidateResumeResponse(BaseModel):
    """Response for validation endpoint"""
    valid: bool
    errors: List[str] = []
    message: Optional[str] = None


class PreviewResumeResponse(BaseModel):
    """Response for preview endpoint"""
    success: bool
    preview_html: str