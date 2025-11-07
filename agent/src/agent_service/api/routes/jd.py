"""
Job Description API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from ...api.schemas.job_description import (
    AnalyzeJDRequest,
    AnalyzeJDResponse,
    JobDescriptionSchema,
    KeywordWeightSchema
)
from ...application.use_cases.analyze_jd import AnalyzeJDUseCase
from ...wiring import get_analyze_jd_use_case

router = APIRouter(prefix="/jd", tags=["Job Description"])

# Import store function
from . import tailor


@router.post("/analyze", response_model=AnalyzeJDResponse)
async def analyze_job_description(
    request: AnalyzeJDRequest,
    use_case: AnalyzeJDUseCase = Depends(get_analyze_jd_use_case)
):
    """
    Analyze job description and extract structured information

    This endpoint:
    1. Extracts company, position, and industry
    2. Identifies required and preferred skills
    3. Extracts responsibilities and qualifications
    4. Generates weighted keywords for matching

    Args:
        request: Job description text

    Returns:
        Analyzed job description with extracted information

    Example:
        ```json
        {
            "raw_text": "Senior Backend Engineer at Acme Corp..."
        }
        ```
    """
    try:
        jd = await use_case.execute(request.raw_text)

        # Convert to schema
        jd_schema = JobDescriptionSchema(
            id=jd.id,
            raw_text=jd.raw_text,
            company=jd.company,
            position=jd.position,
            required_skills=jd.required_skills,
            preferred_skills=jd.preferred_skills,
            responsibilities=jd.responsibilities,
            qualifications=jd.qualifications,
            industry=jd.industry,
            keywords=[
                KeywordWeightSchema(
                    text=kw.text,
                    weight=kw.weight,
                    category=kw.category
                ) for kw in jd.keywords
            ],
            analyzed_at=jd.analyzed_at
        )

        # Store JD for later use in tailoring
        tailor.store_job_description(jd)

        return AnalyzeJDResponse(
            success=True,
            job_description=jd_schema
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error analyzing JD: {e}")
        return AnalyzeJDResponse(
            success=False,
            error=f"Failed to analyze job description: {str(e)}"
        )
