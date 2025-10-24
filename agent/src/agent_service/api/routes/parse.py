"""Resume Parsing API Routes"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ...api.schemas.resume import ParsedResumeSchema
from ...application.use_cases.parse_resume import ParseResumeUseCase
from ...wiring import get_parse_resume_use_case

router = APIRouter(prefix="/parse", tags=["Parse"])


@router.post("/resume", response_model=ParsedResumeSchema)
async def parse_resume(
    file: UploadFile = File(...),
    use_case: ParseResumeUseCase = Depends(get_parse_resume_use_case)
):
    """
    Parse a resume file (PDF or DOCX) and extract structured data

    Args:
        file: Uploaded resume file
        use_case: Parse resume use case (injected)

    Returns:
        Parsed resume data

    Raises:
        HTTPException: If parsing fails
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    allowed_extensions = ['.pdf', '.docx', '.doc']
    file_ext = file.filename.lower().split('.')[-1]
    if f'.{file_ext}' not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )

    try:
        # Read file content
        content = await file.read()

        # Parse resume
        resume = await use_case.execute(content, file.filename)

        # Convert to schema
        return ParsedResumeSchema(
            personal_info={
                "name": resume.personal_info.name if resume.personal_info else None,
                "email": resume.personal_info.email if resume.personal_info else None,
                "phone": resume.personal_info.phone if resume.personal_info else None,
                "linkedin": resume.personal_info.linkedin if resume.personal_info else None,
                "github": resume.personal_info.github if resume.personal_info else None,
            } if resume.personal_info else None,
            experience=[
                {
                    "company": exp.company,
                    "title": exp.title,
                    "location": exp.location,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "description": exp.description,
                }
                for exp in resume.experiences
            ],
            education=[
                {
                    "school": edu.school,
                    "degree": edu.degree,
                    "start_date": edu.start_date,
                    "end_date": edu.end_date,
                    "description": edu.description,
                }
                for edu in resume.education
            ],
            skills=[
                {
                    "name": skill.name,
                    "category": skill.category,
                }
                for skill in resume.skills
            ],
            raw_text=resume.raw_text
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")
