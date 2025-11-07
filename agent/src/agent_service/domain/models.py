from dataclasses import dataclass
from typing import List, Optional, Dict
from dataclasses import field
from datetime import datetime
import uuid


@dataclass
class PersonalInfo:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


@dataclass
class BulletPoint:
    """Single achievement/responsibility bullet point"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    keywords: List[str] = field(default_factory=list)
    skills_used: List[str] = field(default_factory=list)


@dataclass
class Experience:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None  # For backward compatibility
    bullets: List[BulletPoint] = field(default_factory=list)
    skills_used: List[str] = field(default_factory=list)
    industry: Optional[str] = None


@dataclass
class Education:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    school: Optional[str] = None
    degree: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Skill:
    name: Optional[str] = None
    category: Optional[str] = None


@dataclass
class Resume:
    """Basic resume structure (for Phase 1 compatibility)"""
    personal_info: Optional[PersonalInfo] = None
    experiences: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)
    raw_text: Optional[str] = None
    sections: Dict[str, str] = field(default_factory=dict)


@dataclass
class MasterResume:
    """Master resume containing all user's career history"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    personal_info: Optional[PersonalInfo] = None
    experiences: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class KeywordWeight:
    """Weighted keyword from JD analysis"""
    text: str
    weight: float  # 0.0 to 1.0
    category: str  # 'required', 'preferred', 'nice_to_have'


@dataclass
class JobDescription:
    """Analyzed job description"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    raw_text: str = ""
    company: Optional[str] = None
    position: Optional[str] = None
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    qualifications: List[str] = field(default_factory=list)
    industry: Optional[str] = None
    keywords: List[KeywordWeight] = field(default_factory=list)
    analyzed_at: Optional[datetime] = None


@dataclass
class BulletOptimization:
    """Optimization for a single bullet point"""
    bullet_id: str
    original_text: str
    optimized_text: str
    improvements: List[str] = field(default_factory=list)
    keyword_matches: List[str] = field(default_factory=list)
    status: str = "pending"  # 'pending', 'accepted', 'rejected'


@dataclass
class TailoredResume:
    """Customized resume tailored for specific JD"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    master_resume_id: str = ""
    jd_id: str = ""
    personal_info: Optional[PersonalInfo] = None
    selected_experience_ids: List[str] = field(default_factory=list)
    selected_bullet_optimizations: List[BulletOptimization] = field(default_factory=list)
    selected_education_ids: List[str] = field(default_factory=list)
    selected_skills: List[str] = field(default_factory=list)
    match_score: float = 0.0
    ats_score: float = 0.0
    created_at: Optional[datetime] = None
