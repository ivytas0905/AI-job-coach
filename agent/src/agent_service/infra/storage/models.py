"""SQLAlchemy ORM Models for resume optimization system"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base


def generate_uuid():
    """Generate UUID string for primary keys."""
    return str(uuid.uuid4())


class MasterResumeModel(Base):
    """
    Master Resume - stores user's original uploaded resume.

    This is the source of truth for all resume versions.
    """
    __tablename__ = 'master_resumes'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(255), nullable=False, index=True, comment="User ID from Clerk")
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(Text, comment="Path to stored file")

    # Parsed resume data (JSON format)
    parsed_data = Column(JSON, nullable=False, comment="Structured resume data extracted by parser")

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    versions = relationship("ResumeVersionModel", back_populates="master_resume", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MasterResume(id={self.id}, user_id={self.user_id}, filename={self.filename})>"


class ResumeVersionModel(Base):
    """
    Resume Version - stores optimized versions of the master resume.

    Each version can be customized for different companies or job types.
    """
    __tablename__ = 'resume_versions'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    master_resume_id = Column(String(36), ForeignKey('master_resumes.id'), nullable=False, index=True)

    # Version metadata
    version_name = Column(String(255), nullable=False, comment="e.g., 'Google MLE v1', 'Generic SWE v2'")
    description = Column(Text, comment="What's special about this version")

    # Customization
    company = Column(String(255), index=True, comment="Company name if company-specific")
    job_title = Column(String(255), index=True, comment="Target job title")

    # Content (JSON format)
    # Structure: { "personal_info": {...}, "experiences": [...], "education": [...], "skills": [...] }
    content = Column(JSON, nullable=False, comment="Customized resume content")

    # Optimization metadata
    target_keywords = Column(JSON, comment="List of target keywords used for optimization")
    jd_analysis_id = Column(String(36), ForeignKey('jd_analyses.id'), comment="Reference to JD analysis if used")

    # Scores
    ats_score = Column(Integer, comment="ATS compatibility score (0-100)")
    keyword_match_score = Column(Float, comment="Keyword matching score (0.0-1.0)")

    # Status
    status = Column(String(50), default='draft', comment="draft|finalized|applied")
    applied_at = Column(DateTime, comment="When this version was used for application")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    master_resume = relationship("MasterResumeModel", back_populates="versions")
    jd_analysis = relationship("JDAnalysisModel", back_populates="resume_versions")
    chat_sessions = relationship("ChatSessionModel", back_populates="resume_version")

    def __repr__(self):
        return f"<ResumeVersion(id={self.id}, name={self.version_name}, company={self.company})>"


class JDAnalysisModel(Base):
    """
    Job Description Analysis - caches JD analysis results.

    This avoids re-analyzing the same JD multiple times.
    """
    __tablename__ = 'jd_analyses'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(255), nullable=False, index=True)

    # JD metadata
    company = Column(String(255), index=True)
    job_title = Column(String(255), nullable=False, index=True)
    job_url = Column(Text, comment="URL to job posting")

    # Raw JD text
    raw_text = Column(Text, nullable=False, comment="Original job description text")
    jd_hash = Column(String(64), index=True, unique=True, comment="Hash of JD text for caching")

    # Analysis results (JSON format)
    # Structure: {
    #   "top_keywords": [{"keyword": str, "weight": float, "type": str}, ...],
    #   "required_skills": [...],
    #   "preferred_skills": [...],
    #   "common_verbs": [...],
    #   "industry": str
    # }
    analysis_result = Column(JSON, nullable=False, comment="Extracted keywords and insights")

    # Timestamps
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    resume_versions = relationship("ResumeVersionModel", back_populates="jd_analysis")

    def __repr__(self):
        return f"<JDAnalysis(id={self.id}, company={self.company}, job_title={self.job_title})>"


class ChatSessionModel(Base):
    """
    Chat Session - stores conversation history with AI assistant.

    Each session is tied to a specific resume version for context.
    """
    __tablename__ = 'chat_sessions'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(255), nullable=False, index=True)
    resume_version_id = Column(String(36), ForeignKey('resume_versions.id'), index=True, comment="Context for chat")

    # Session metadata
    session_name = Column(String(255), comment="Optional session name")

    # Messages (JSON format)
    # Structure: [{"role": "user"|"assistant", "content": str, "timestamp": str}, ...]
    messages = Column(JSON, nullable=False, default=list, comment="Chat message history")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resume_version = relationship("ResumeVersionModel", back_populates="chat_sessions")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, resume_version_id={self.resume_version_id})>"


class OptimizationHistoryModel(Base):
    """
    Optimization History - tracks all optimization suggestions and user actions.

    Helps understand which optimizations are most useful.
    """
    __tablename__ = 'optimization_history'

    id = Column(String(36), primary_key=True, default=generate_uuid)
    resume_version_id = Column(String(36), ForeignKey('resume_versions.id'), nullable=False, index=True)

    # Optimization details
    section = Column(String(50), comment="experience|skills|summary")
    item_index = Column(Integer, comment="Index of bullet point or item")

    # Content
    original_text = Column(Text, nullable=False)
    optimized_text = Column(Text, nullable=False)

    # Optimization metadata
    optimization_type = Column(String(50), comment="star|keywords|quantification")
    improvements = Column(JSON, comment="List of improvement descriptions")
    target_keywords = Column(JSON, comment="Keywords incorporated")

    # User action
    user_action = Column(String(20), comment="accepted|rejected|modified")
    modified_text = Column(Text, comment="If user modified the suggestion")

    # Timestamps
    suggested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    actioned_at = Column(DateTime, comment="When user took action")

    def __repr__(self):
        return f"<OptimizationHistory(id={self.id}, type={self.optimization_type}, action={self.user_action})>"
