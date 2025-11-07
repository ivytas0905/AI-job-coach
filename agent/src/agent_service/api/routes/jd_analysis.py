"""JD Analysis API Routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.use_cases.jd_analysis_enhanced import JDAnalysisEnhancedUseCase
from ...infra.llm.enhanced_llm import EnhancedLLMService
from ...infra.cache.memory_cache import MemoryCacheService, get_cache_service
from ...infra.storage.database import get_db_session
from ..schemas.jd_analysis_schemas import (
    AnalyzeJDRequest,
    JDAnalysisResponse,
    JDAnalysisHistoryResponse
)

router = APIRouter(prefix="/jd-analysis", tags=["JD Analysis"])


# Dependency to get LLM service
def get_llm_service():
    """Get LLM service instance."""
    from ...config import get_settings
    settings = get_settings()
    return EnhancedLLMService(api_key=settings.openai_api_key)


# Dependency to get use case
async def get_jd_analysis_use_case(
    db: AsyncSession = Depends(get_db_session),
    llm_service: EnhancedLLMService = Depends(get_llm_service),
    cache_service: MemoryCacheService = Depends(get_cache_service)
) -> JDAnalysisEnhancedUseCase:
    """Get JD analysis use case with all dependencies."""
    return JDAnalysisEnhancedUseCase(
        llm_service=llm_service,
        cache_service=cache_service,
        db_session=db
    )


@router.post(
    "/analyze",
    response_model=JDAnalysisResponse,
    summary="Analyze Job Description",
    description="""
    Analyze a job description and extract key information.

    **Features:**
    - Extracts TOP 20 keywords with importance weights
    - Identifies required vs preferred skills
    - Extracts common action verbs and domain terms
    - Caches results to avoid redundant API calls

    **Returns:**
    - Structured analysis with keywords, skills, and metadata
    - Cached flag indicates if result was retrieved from cache
    """
)
async def analyze_jd(
    request: AnalyzeJDRequest,
    use_case: JDAnalysisEnhancedUseCase = Depends(get_jd_analysis_use_case),
    user_id: str = "anonymous"  # TODO: Get from Clerk authentication
) -> JDAnalysisResponse:
    """
    Analyze job description and extract keywords.

    This endpoint uses GPT-4 to analyze the JD and extract the most important
    keywords for ATS optimization. Results are cached to reduce API costs.
    """
    try:
        result = await use_case.execute(
            jd_text=request.jd_text,
            job_title=request.job_title,
            company=request.company,
            job_url=request.job_url,
            user_id=user_id
        )

        return JDAnalysisResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD analysis failed: {str(e)}")


@router.get(
    "/{jd_id}",
    response_model=JDAnalysisResponse,
    summary="Get JD Analysis by ID",
    description="Retrieve a previously analyzed job description by its ID"
)
async def get_jd_analysis(
    jd_id: str,
    use_case: JDAnalysisEnhancedUseCase = Depends(get_jd_analysis_use_case)
):
    """Get JD analysis by ID from database."""
    result = await use_case.get_analysis_by_id(jd_id)

    if result is None:
        raise HTTPException(status_code=404, detail=f"JD analysis {jd_id} not found")

    return result


@router.get(
    "/history/user",
    response_model=JDAnalysisHistoryResponse,
    summary="Get User's JD Analysis History",
    description="Get list of all JD analyses performed by the current user"
)
async def get_user_history(
    limit: int = 10,
    use_case: JDAnalysisEnhancedUseCase = Depends(get_jd_analysis_use_case),
    user_id: str = "anonymous"  # TODO: Get from Clerk authentication
):
    """Get user's JD analysis history."""
    analyses = await use_case.get_user_analysis_history(user_id, limit)

    return JDAnalysisHistoryResponse(
        analyses=analyses,
        total=len(analyses)
    )
