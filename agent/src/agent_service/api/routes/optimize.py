"""HTTP adapters for AI-assisted resume content enhancement."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ...application.use_cases.enhance_content import (
    EnhanceContentInput,
    EnhanceContentUseCase,
    EnhanceSummaryInput,
)
from ...wiring import get_enhance_content_use_case

router = APIRouter(prefix="/resume", tags=["optimize"])


class EnhanceRequest(BaseModel):
    description: str
    jobTitle: Optional[str] = None
    company: Optional[str] = None


class EnhanceSummaryRequest(BaseModel):
    summary: str
    targetJob: Optional[str] = None
    skills: Optional[List[str]] = None
    yearsOfExperience: Optional[int] = None


class EnhanceResponse(BaseModel):
    success: bool
    enhanced: str


@router.post("/enhance", response_model=EnhanceResponse)
async def enhance_content(
    request: EnhanceRequest,
    use_case: EnhanceContentUseCase = Depends(get_enhance_content_use_case),
):
    try:
        result = await use_case.enhance_experience(
            EnhanceContentInput(
                description=request.description,
                job_title=request.jobTitle,
                company=request.company,
            )
        )
        return EnhanceResponse(success=True, enhanced=result.enhanced)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to enhance content") from exc


@router.post("/enhance-summary", response_model=EnhanceResponse)
async def enhance_summary(
    request: EnhanceSummaryRequest,
    use_case: EnhanceContentUseCase = Depends(get_enhance_content_use_case),
):
    try:
        result = await use_case.enhance_summary(
            EnhanceSummaryInput(
                summary=request.summary,
                target_job=request.targetJob,
                skills=tuple(request.skills or ()),
                years_of_experience=request.yearsOfExperience,
            )
        )
        return EnhanceResponse(success=True, enhanced=result.enhanced)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to enhance summary") from exc
