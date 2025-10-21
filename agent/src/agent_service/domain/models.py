from dataclasses import dataclass
from typing import List, Optional, Dict
from dataclasses import field
from enum import Enum


class ResumeSource(Enum):
    """简历来源"""
    BUILT = "built_from_scratch"
    UPLOADED = "uploaded_file"

class ExperienceType(Enum):
    """经历类型"""
    WORK = "work"
    INTERNSHIP = "internship"
    PROJECT = "project"
    VOLUNTEER = "volunteer"


@dataclass
class PersonalInfo:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None

@dataclass
class Experience:
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

    


@dataclass
class Education:
    school: Optional[str] = None
    degree: Optional[str] = None
    major: Optional[str] = None  
    gpa: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

    

@dataclass
class Skill:
    name: Optional[str] = None
    category: Optional[str] = None
    
    
    

@dataclass
class Resume:
    personal_info: Optional[PersonalInfo] = None
    experiences: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)
    raw_text: Optional[str] = None
    sections: Dict[str, str] = field(default_factory=dict)

    

    