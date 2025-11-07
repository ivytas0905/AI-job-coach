"""
Tailor Resume API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from ...api.schemas.tailored_resume import (
    TailorResumeRequest,
    TailorResumeResponse,
    TailoredResumeSchema,
    BulletOptimizationSchema
)
from ...api.schemas.job_description import JobDescriptionSchema, KeywordWeightSchema
from ...application.use_cases.tailor_resume import TailorResumeUseCase
from ...domain.models import TailoredResume, JobDescription, MasterResume
from ...wiring import get_tailor_resume_use_case

router = APIRouter(prefix="/tailor", tags=["Tailored Resume"])

# In-memory storage for MVP
tailored_resumes: Dict[str, TailoredResume] = {}
job_descriptions: Dict[str, JobDescription] = {}

# Import master resumes storage from master.py
from .master import master_resumes


@router.post("/resume", response_model=TailorResumeResponse)
async def tailor_resume(
    request: TailorResumeRequest,
    use_case: TailorResumeUseCase = Depends(get_tailor_resume_use_case)
):
    """
    Create a tailored resume from master resume based on JD

    This endpoint:
    1. Selects most relevant experiences from master resume
    2. Selects best bullet points for each experience
    3. Optimizes bullets using STAR framework and JD keywords
    4. Calculates match score and ATS score

    Args:
        request: Master resume ID and JD ID

    Returns:
        Tailored resume with optimized content

    Example:
        ```json
        {
            "master_resume_id": "master-123",
            "jd_id": "jd-456"
        }
        ```
    """
    try:
        # Get master resume
        if request.master_resume_id not in master_resumes:
            raise HTTPException(status_code=404, detail="Master resume not found")

        master = master_resumes[request.master_resume_id]

        # Get job description
        if request.jd_id not in job_descriptions:
            raise HTTPException(status_code=404, detail="Job description not found")

        jd = job_descriptions[request.jd_id]

        # Create tailored resume
        tailored = await use_case.execute(master, jd)

        # Store tailored resume
        tailored_resumes[tailored.id] = tailored

        # Convert to schema
        tailored_schema = _tailored_to_schema(tailored)

        return TailorResumeResponse(
            success=True,
            tailored_resume=tailored_schema
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error tailoring resume: {e}")
        import traceback
        traceback.print_exc()
        return TailorResumeResponse(
            success=False,
            error=f"Failed to tailor resume: {str(e)}"
        )


@router.get("/resume/{tailored_id}", response_model=TailoredResumeSchema)
async def get_tailored_resume(tailored_id: str):
    """
    Get a tailored resume by ID

    Args:
        tailored_id: Tailored resume ID

    Returns:
        Tailored resume
    """
    if tailored_id not in tailored_resumes:
        raise HTTPException(status_code=404, detail="Tailored resume not found")

    tailored = tailored_resumes[tailored_id]
    return _tailored_to_schema(tailored)


def _tailored_to_schema(tailored: TailoredResume) -> TailoredResumeSchema:
    """Convert TailoredResume domain model to schema"""
    return TailoredResumeSchema(
        id=tailored.id,
        master_resume_id=tailored.master_resume_id,
        jd_id=tailored.jd_id,
        selected_experience_ids=tailored.selected_experience_ids,
        selected_bullet_optimizations=[
            BulletOptimizationSchema(
                bullet_id=opt.bullet_id,
                original_text=opt.original_text,
                optimized_text=opt.optimized_text,
                improvements=opt.improvements,
                keyword_matches=opt.keyword_matches,
                status=opt.status
            ) for opt in tailored.selected_bullet_optimizations
        ],
        selected_education_ids=tailored.selected_education_ids,
        selected_skills=tailored.selected_skills,
        match_score=tailored.match_score,
        ats_score=tailored.ats_score,
        created_at=tailored.created_at
    )


# Helper function to store JD (called from jd.py route)
def store_job_description(jd: JobDescription):
    """Store job description for later use"""
    job_descriptions[jd.id] = jd
