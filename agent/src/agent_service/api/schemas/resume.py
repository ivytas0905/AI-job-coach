from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

class PersonalInfoSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None

class ExperienceSchema(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    
class EducationSchema(BaseModel):
    school: Optional[str] = None
    degree: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    
class SkillSchema(BaseModel):
    name: str
    category: Optional[str] = None

class ParsedResumeSchema(BaseModel):
    personal_info: Optional[PersonalInfoSchema] = None
    experience: List[ExperienceSchema] = []
    education: List[EducationSchema] = []
    skills: List[SkillSchema] = []
    raw_text: Optional[str] = None

