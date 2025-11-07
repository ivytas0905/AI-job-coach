from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class BulletPointSchema(BaseModel):
    """Schema for bullet point"""
    id: Optional[str] = None
    text: str
    keywords: List[str] = Field(default_factory=list)
    skills_used: List[str] = Field(default_factory=list)


class ExperienceSchema(BaseModel):
    """Schema for experience with bullets"""
    id: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None  # For backward compatibility
    bullets: List[BulletPointSchema] = Field(default_factory=list)
    skills_used: List[str] = Field(default_factory=list)
    industry: Optional[str] = None


class EducationSchema(BaseModel):
    """Schema for education"""
    id: Optional[str] = None
    school: Optional[str] = None
    degree: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class SkillSchema(BaseModel):
    """Schema for skill"""
    name: str
    category: Optional[str] = None


class PersonalInfoSchema(BaseModel):
    """Schema for personal information"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


class MasterResumeSchema(BaseModel):
    """Schema for master resume"""
    id: Optional[str] = None
    user_id: Optional[str] = None
    personal_info: Optional[PersonalInfoSchema] = None
    experiences: List[ExperienceSchema] = Field(default_factory=list)
    education: List[EducationSchema] = Field(default_factory=list)
    skills: List[SkillSchema] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "personal_info": {
                    "name": "John Doe",
                    "email": "john@example.com"
                },
                "experiences": [
                    {
                        "company": "Google",
                        "title": "Senior Software Engineer",
                        "start_date": "2021-01",
                        "end_date": "2023-12",
                        "bullets": [
                            {
                                "text": "Led migration of monolithic architecture to microservices",
                                "keywords": ["microservices", "architecture", "leadership"],
                                "skills_used": ["Kubernetes", "Docker", "Python"]
                            }
                        ],
                        "skills_used": ["Python", "Kubernetes", "Docker"],
                        "industry": "Tech"
                    }
                ]
            }
        }


class CreateMasterResumeRequest(BaseModel):
    """Request to create master resume from parsed resume"""
    personal_info: Optional[PersonalInfoSchema] = None
    experiences: List[ExperienceSchema] = Field(default_factory=list)
    education: List[EducationSchema] = Field(default_factory=list)
    skills: List[SkillSchema] = Field(default_factory=list)


class UpdateMasterResumeRequest(BaseModel):
    """Request to update master resume"""
    personal_info: Optional[PersonalInfoSchema] = None
    experiences: Optional[List[ExperienceSchema]] = None
    education: Optional[List[EducationSchema]] = None
    skills: Optional[List[SkillSchema]] = None


class AddExperienceRequest(BaseModel):
    """Request to add experience"""
    experience: ExperienceSchema


class UpdateExperienceRequest(BaseModel):
    """Request to update experience"""
    experience: ExperienceSchema


class AddBulletPointRequest(BaseModel):
    """Request to add bullet point to experience"""
    experience_id: str
    bullet: BulletPointSchema


class UpdateBulletPointRequest(BaseModel):
    """Request to update bullet point"""
    experience_id: str
    bullet_id: str
    bullet: BulletPointSchema
