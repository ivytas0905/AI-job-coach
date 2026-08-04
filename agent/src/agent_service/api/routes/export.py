"""
Export resume to PDF/Word
Shared endpoint used by both Build and Upload workflows
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, Any, Literal

from ...application.use_cases.export_resume import ExportResumeUseCase
from ...infra.generators.pdf_generator import PDFGenerator
from ...infra.generators.word_generator import WordGenerator
from ...domain.models import ResumeSource, Resume, PersonalInfo, Experience, Education, Skill
from ...utils.http import content_disposition_for_filename

router = APIRouter(prefix="/api/resume", tags=["export"])

# ============= Request Schema =============
class ContactInfo(BaseModel):
    """Contact information from frontend"""
    fullName: str
    email: str
    phone: str
    location: str = ""
    title: str = ""


class ExperienceInfo(BaseModel):
    """Experience entry from frontend"""
    position: str
    company: str
    startDate: str
    endDate: str = ""
    location: str = ""
    description: str = ""

class EducationInfo(BaseModel):
    """Education entry from frontend"""
    degree: str
    school: str
    startDate: str
    endDate: str = ""
    location: str = ""


class ResumeData(BaseModel):
    """Complete resume data"""
    contact: ContactInfo
    experience: list[ExperienceInfo]
    education: list[EducationInfo]
    skills: list[str]
    summary: str = ""


class GenerateResumeRequest(BaseModel):
    """Request to generate resume file"""
    resumeData: ResumeData
    template: str  # "professional", "simple", "modern"
    format: Literal['pdf', 'word']

# ============= API Endpoints =============
@router.post("/generate")
async def generate_resume(request: GenerateResumeRequest):
    """
    Generate resume file (PDF or Word)
    
    This endpoint is shared by:
    - Build Resume workflow (form-based creation)
    - Upload Resume workflow (file upload + optimization)
    
    Args:
        request: GenerateResumeRequest containing resume data, template, and format
        
    Returns:
        File download response (PDF or DOCX)
    """
    try:
        # 1. Convert frontend data to domain model
        resume = _convert_to_domain_model(request.resumeData)
        
        # 2. Create generators
        pdf_gen = PDFGenerator()
        word_gen = WordGenerator()
        
        # 3. Create export use case
        export_use_case = ExportResumeUseCase(
            pdf_generator=pdf_gen,
            word_generator=word_gen
        )
        
        # 4. Generate file
        file_content = export_use_case.execute(
            resume=resume,
            format=request.format,
            template=request.template
        )
        
        # 5. Set appropriate media type
        if request.format == 'pdf':
            media_type = 'application/pdf'
            file_extension = 'pdf'
        else:
            media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            file_extension = 'docx'
        
        # 6. Generate filename
        filename = f"resume_{request.resumeData.contact.fullName.replace(' ', '_')}.{file_extension}"
        
        # 7. Return file as download
        return Response(
            content=file_content,
            media_type=media_type,
            headers={
                'Content-Disposition': content_disposition_for_filename(filename),
                'Access-Control-Expose-Headers': 'Content-Disposition'
            }
        )
        
    except Exception as e:
        print(f"Error generating resume: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate resume: {str(e)}"
        )
#诊断
# === 1) 运行时确认你导入到的到底是哪一个 Resume ===
# import inspect, dataclasses, sys
# from pydantic import BaseModel

# print("=== [DEBUG Resume] ===")
# print("type(Resume):", type(Resume))
# print("Resume.__module__:", getattr(Resume, "__module__", None))
# print("Resume source file:", inspect.getsourcefile(Resume))
# print("is_dataclass:", dataclasses.is_dataclass(Resume))
# print("is_pydantic_model:", issubclass(Resume, BaseModel) if isinstance(Resume, type) else False)
# print("annotations:", getattr(Resume, "__annotations__", {}))
# try:
#     print("signature:", inspect.signature(Resume))
# except Exception as e:
#     print("signature error:", repr(e))
# print("=======================")

# ============= Helper Functions =============
def _convert_to_domain_model(resume_data: ResumeData) -> Resume:
    """
    Convert frontend ResumeData to domain Resume model
    
    Args:
        resume_data: ResumeData from frontend
        
    Returns:
        Resume domain model
    """
    # Convert contact info
    personal_info = PersonalInfo(
        fullname=resume_data.contact.fullName,
        email=resume_data.contact.email,
        phone=resume_data.contact.phone,
        location=resume_data.contact.location or None,
        title=resume_data.contact.title or None
    )

    # Convert experiences
    experiences = []
    for exp in resume_data.experience:
        experiences.append(Experience(
            title=exp.position,
            company=exp.company,
            start_date=exp.startDate,
            end_date=exp.endDate if exp.endDate else None,
            location=exp.location or None,
            description=exp.description or "",
            type="work"  # 根据你的 ExperienceType 定义
        ))
    
    # Convert education
    education_list = []
    for edu in resume_data.education:
        education_list.append(Education(
            degree=edu.degree,
            school=edu.school,
            start_date=edu.startDate,
            end_date=edu.endDate if edu.endDate else None,
            location=edu.location or None
        ))

    # Convert skills
    skills = [Skill(name=skill) for skill in resume_data.skills]
    
    # Create Resume object
    resume = Resume(
        source=ResumeSource.BUILT,
        personal_info=personal_info,
        experiences=experiences,
        education=education_list,
        skills=skills,
        summary=resume_data.summary or "",
        target_job=None
    )
    
    return resume   
    
