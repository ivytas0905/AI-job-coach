"""
Build Resume API routes
Handles resume construction from form data
Does NOT handle file export (see export.py)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from dataclasses import asdict


from application.use_cases.build_resume import BuildResumeUseCase
from domain.models import (
    Resume, 
    PersonalInfo, 
    Experience, 
    Education, 
    Skill,
    ExperienceType, 
    ResumeSource
)
# Import your LLM service, retriever, template engine later
# from infra.llm.openai_provider import OpenAIProvider

router = APIRouter(prefix="/api/resume/build", tags=["build"])


# ============= Request Models =============

class ContactInfo(BaseModel):
    """Contact information from frontend"""
    fullName: str
    email: str
    phone: str
    location: Optional[str] = None
    title: Optional[str] = None


class ExperienceInfo(BaseModel):
    """Experience entry from frontend"""
    position: str
    company: str
    startDate: str
    endDate: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class EducationInfo(BaseModel):
    """Education entry from frontend"""
    degree: str
    school: str
    startDate: str
    endDate: Optional[str] = None,
    location: Optional[str] = None

    


class BuildResumeRequest(BaseModel):
    """Complete resume data from frontend form"""
    contact: ContactInfo
    experience: List[ExperienceInfo]
    education: List[EducationInfo]
    skills: List[str]
    summary: Optional[str] = None
    targetJob: Optional[str] = None
    enhanceWithAI: bool = False  # Whether to use AI enhancement


# ============= API Endpoints =============

@router.post("/")
async def build_resume(request: BuildResumeRequest):
    """
    Build resume from form data
    
    This endpoint:
    1. Receives form data from frontend
    2. Converts to domain model
    3. Optionally enhances with AI
    4. Returns structured data for preview
    
    Note: File generation (PDF/Word) is handled by /api/resume/generate
    """
    try:
        # Convert frontend data to domain model
        resume = _convert_to_domain_model(request)
        
        # Create use case (inject dependencies)
        # For now, pass None if services aren't ready
        build_use_case = BuildResumeUseCase(
            llm_service=None,  # TODO: Inject actual LLM service
            retriever=None,    # TODO: Inject actual retriever
            template_engine=None  # TODO: Inject actual template engine
        )
        
        # Execute use case
        result = build_use_case.execute(request)
        preview_html = result.get("preview_html")
        if preview_html is None:
            preview_html = _generate_simple_preview_html(resume)

        return {
            "success": True,
            "resume": result["resume"],
            "preview_html": preview_html,  # If template engine is ready
            "message": "Resume built successfully"
        }
        
    except Exception as e:
        print(f"Error building resume: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to build resume: {str(e)}"
        )


@router.post("/validate")
async def validate_resume_data(request: BuildResumeRequest):
    """
    Validate resume data without building
    
    Useful for real-time validation as user fills the form
    """
    try:
        errors = []
        
        # Validate contact info
        if not request.contact.fullName:
            errors.append("Full name is required")
        if not request.contact.email:
            errors.append("Email is required")
        if not request.contact.phone:
            errors.append("Phone is required")
        
        # Validate experience
        if not request.experience or len(request.experience) == 0:
            errors.append("At least one experience entry is required")
        
        # Validate education
        if not request.education or len(request.education) == 0:
            errors.append("At least one education entry is required")
        
        # Validate skills
        if not request.skills or len(request.skills) == 0:
            errors.append("At least one skill is required")
        
        if errors:
            return {
                "valid": False,
                "errors": errors
            }
        
        return {
            "valid": True,
            "message": "Resume data is valid"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/preview")
async def generate_preview(request: BuildResumeRequest):
    """
    Generate HTML preview of resume
    
    Used for showing preview before download
    Returns HTML string that can be rendered in frontend
    """
    try:
        # Convert to domain model
        resume = _convert_to_domain_model(request)
        
        # Generate preview HTML
        # For now, return a simple preview
        # TODO: Use template engine when ready
        preview_html = _generate_simple_preview_html(resume)
        
        return {
            "success": True,
            "preview_html": preview_html
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate preview: {str(e)}"
        )


# ============= Helper Functions =============

def _convert_to_domain_model(request: BuildResumeRequest) -> Resume:
    """
    Convert frontend request data to domain model
    
    Args:
        request: BuildResumeRequest from frontend
        
    Returns:
        Resume domain model
    """
    # Convert contact info
    personal_info = PersonalInfo(
        fullname=request.contact.fullName,
        email=request.contact.email,
        phone=request.contact.phone,
        location=request.contact.location,
        title=request.contact.title
    )
    
    # Convert experiences
    experiences = []
    for exp in request.experience:
        experiences.append(Experience(
            type="WORK", 
            title=exp.position,
            company=exp.company,
            start_date=exp.startDate,
            end_date=exp.endDate,
            location=exp.location,
            description=exp.description or ""
        ))
    
    # Convert education
    education_list = []
    for edu in request.education:
        education_list.append(Education(
            degree=edu.degree,
            school=edu.school,
            start_date=edu.startDate,
            end_date=edu.endDate,
            location=edu.location
        ))
    
    # Convert skills
    skills = [Skill(name=skill) for skill in request.skills]
    
    # Create Resume object
    resume = Resume(
        #source=ResumeSource.BUILT,  # Adjust based on your ResumeSource enum
        personal_info=personal_info,
        experiences=experiences,
        education=education_list,
        skills=skills,
        summary=request.summary or "",
        target_job=request.targetJob
    )
    
    return resume


def _generate_simple_preview_html(resume: Resume) -> str:
    """
    Generate simple HTML preview
    
    TODO: Replace with proper template engine
    """
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
        <!-- Contact Info -->
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="margin: 0;">{resume.personal_info.fullname}</h1>
            <h3 style="margin: 10px 0; color: #666;">{resume.personal_info.title or ''}</h3>
            <p style="margin: 5px 0;">
                {resume.personal_info.email} | {resume.personal_info.phone} | {resume.personal_info.location or ''}
            </p>
        </div>
        
        <!-- Target Job -->
        {f'<div style="margin-bottom: 30px; text-align: center;"><h2 style="color: #2563eb; margin-bottom: 10px;">Target Position</h2><p style="font-size: 18px; font-weight: 600;">{resume.target_job}</p></div>' if resume.target_job else ''}
        
        <!-- Summary -->
        {f'<div style="margin-bottom: 30px;"><h2>Summary</h2><p>{resume.summary}</p></div>' if resume.summary else ''}
        
        <!-- Experience -->
        <div style="margin-bottom: 30px;">
            <h2>Experience</h2>
            {''.join([f'''
                <div style="margin-bottom: 20px;">
                    <h3 style="margin: 5px 0;">{exp.title} - {exp.company}</h3>
                    <p style="margin: 5px 0; color: #666; font-style: italic;">
                        {exp.start_date} - {exp.end_date or 'Present'} | {exp.location or ''}
                    </p>
                    <p style="margin: 10px 0;">{exp.description}</p>
                </div>
            ''' for exp in resume.experiences])}
        </div>
        
        <!-- Education -->
        <div style="margin-bottom: 30px;">
            <h2>Education</h2>
            {''.join([f'''
                <div style="margin-bottom: 15px;">
                    <h3 style="margin: 5px 0;">{edu.degree} - {edu.school}</h3>
                    <p style="margin: 5px 0; color: #666; font-style: italic;">
                        {edu.start_date} - {edu.end_date or 'Present'}
                    </p>
                </div>
            ''' for edu in resume.education])}
        </div>
        
        <!-- Skills -->
        <div>
            <h2>Skills</h2>
            <p>{' • '.join([skill.name for skill in resume.skills])}</p>
        </div>
    </div>
    """
    
    return html
