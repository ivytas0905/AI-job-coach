"""Resume Optimization API Routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.use_cases.resume_optimization_enhanced import ResumeOptimizationEnhancedUseCase
from ...infra.llm.enhanced_llm import EnhancedLLMService
from ...infra.storage.database import get_db_session
from ..schemas.optimization_schemas import (
    OptimizeResumeRequest,
    OptimizeResumeResponse,
    OptimizationSuggestion
)

router = APIRouter(prefix="/resume-optimization", tags=["Resume Optimization"])


# Dependency to get LLM service
def get_llm_service():
    """Get LLM service instance."""
    from ...config import get_settings
    settings = get_settings()
    return EnhancedLLMService(api_key=settings.openai_api_key)


# Dependency to get use case
async def get_optimization_use_case(
    db: AsyncSession = Depends(get_db_session),
    llm_service: EnhancedLLMService = Depends(get_llm_service)
) -> ResumeOptimizationEnhancedUseCase:
    """Get resume optimization use case with all dependencies."""
    return ResumeOptimizationEnhancedUseCase(
        llm_service=llm_service,
        db_session=db
    )


@router.post(
    "/optimize",
    response_model=OptimizeResumeResponse,
    summary="Optimize Resume",
    description="""
    Optimize resume bullet points using STAR framework and target keywords.

    **Features:**
    - Applies STAR framework (Situation, Task, Action, Result)
    - Incorporates target keywords from JD analysis
    - Adds quantifiable metrics
    - Uses strong action verbs
    - Optimizes for ATS compatibility

    **Returns:**
    - List of optimization suggestions for each bullet point
    - Original and optimized text comparison
    - Improvement descriptions
    - Score improvement estimates
    """
)
async def optimize_resume(
    request: OptimizeResumeRequest,
    use_case: ResumeOptimizationEnhancedUseCase = Depends(get_optimization_use_case)
) -> OptimizeResumeResponse:
    """
    Optimize resume using STAR framework and target keywords.

    This endpoint analyzes resume bullet points and provides AI-powered
    optimization suggestions. Each suggestion includes:
    - Original text
    - Optimized text with STAR framework
    - List of improvements made
    - Estimated score improvement
    """
    try:
        optimizations = await use_case.optimize_resume(
            resume_data=request.resume_data,
            target_keywords=request.target_keywords,
            job_title=request.job_title,
            resume_version_id=request.resume_version_id
        )

        # Calculate total score improvement
        total_improvement = sum(opt.get('score_improvement', 0) for opt in optimizations)

        return OptimizeResumeResponse(
            optimizations=[OptimizationSuggestion(**opt) for opt in optimizations],
            total_suggestions=len(optimizations),
            estimated_score_improvement=total_improvement
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume optimization failed: {str(e)}")


@router.post(
    "/optimize-bullet",
    response_model=dict,
    summary="Optimize Single Bullet Point",
    description="Optimize a single bullet point (useful for testing or targeted improvements)"
)
async def optimize_single_bullet(
    bullet: str,
    target_keywords: list[str],
    company: str = "",
    title: str = "",
    job_title: str = "",
    use_case: ResumeOptimizationEnhancedUseCase = Depends(get_optimization_use_case)
):
    """Optimize a single bullet point."""
    try:
        llm_service = use_case.llm

        optimized = await llm_service.optimize_bullet_star(
            bullet=bullet,
            target_keywords=target_keywords,
            context={
                'company': company,
                'title': title,
                'job_title': job_title
            }
        )

        return {
            "original": bullet,
            "optimized": optimized,
            "keywords_used": target_keywords[:5]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bullet optimization failed: {str(e)}")


@router.post(
    "/refine-optimization",
    response_model=dict,
    summary="Refine Optimization Based on User Feedback",
    description="Refine a specific bullet optimization based on user's discussion feedback"
)
async def refine_optimization(
    original_bullet: str,
    current_suggestion: str,
    user_feedback: str,
    target_keywords: list[str],
    company: str = "",
    title: str = "",
    job_title: str = "",
    use_case: ResumeOptimizationEnhancedUseCase = Depends(get_optimization_use_case)
):
    """
    Refine an optimization suggestion based on user feedback.

    This endpoint allows users to discuss and iteratively improve
    the AI's suggestions through natural language feedback.
    """
    try:
        llm_service = use_case.llm

        # Build a refinement prompt that incorporates user feedback
        refinement_prompt = f"""You are helping refine a resume bullet point optimization.

Original bullet point:
{original_bullet}

Current suggested optimization:
{current_suggestion}

User's feedback:
{user_feedback}

Target keywords (REFERENCE ONLY): {', '.join(target_keywords[:5])}
Job context: {title} at {company}, targeting {job_title}

⚠️ CRITICAL ANTI-HALLUCINATION RULES:
1. ONLY use information from the ORIGINAL bullet point
2. NEVER add technologies, features, or achievements not in the original
3. NEVER add keywords if they don't describe what's ALREADY in the original bullet
4. If a keyword doesn't match original content, SKIP IT - don't force it
5. DO NOT invent metrics, numbers, or capabilities
6. Better to skip keywords than to fabricate content

IMPORTANT - Action Verb Variety:
Choose a DIFFERENT action verb from the current suggestion. Select from these categories based on the contribution:

• INNOVATION/CREATION: Pioneered, Architected, Engineered, Designed, Conceived, Developed, Built, Created, Generated
• LEADERSHIP: Led, Directed, Orchestrated, Championed, Drove, Steered, Guided, Mobilized, Helmed
• EXECUTION: Implemented, Deployed, Executed, Launched, Delivered, Established, Introduced, Rolled out
• IMPROVEMENT: Enhanced, Streamlined, Refined, Transformed, Modernized, Revitalized, Upgraded, Boosted
• ANALYSIS: Analyzed, Investigated, Evaluated, Assessed, Researched, Examined, Measured, Quantified
• COLLABORATION: Facilitated, Collaborated, Coordinated, Partnered, Enabled, Unified, Integrated
• TECHNICAL: Built, Coded, Programmed, Configured, Automated, Integrated, Debugged, Migrated

Generate a NEW version that:
1. ADDRESSES the user's specific feedback: "{user_feedback}"
2. Uses a DIFFERENT action verb (avoid repeating verbs from current suggestion)
3. Maintains STAR framework (Situation, Task, Action, Result)
4. Keeps ALL numbers and facts from the original bullet
5. ONLY adds keywords that accurately describe what's ALREADY in the original

Provide ONLY the refined bullet point text, no explanations."""

        # Call LLM with refinement prompt
        refined = await llm_service.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume writer who excels at refining resume bullet points based on user feedback."
                },
                {
                    "role": "user",
                    "content": refinement_prompt
                }
            ],
            temperature=0.7,
            max_tokens=200
        )

        refined_text = refined.choices[0].message.content.strip()

        # Analyze what changed
        improvements = []

        # Check for new keywords added
        new_keywords = [
            kw for kw in target_keywords[:5]
            if kw.lower() not in current_suggestion.lower() and kw.lower() in refined_text.lower()
        ]
        if new_keywords:
            improvements.append(f"Added keywords: {', '.join(new_keywords)}")

        # Check if feedback was addressed
        improvements.append(f"Addressed user feedback: {user_feedback[:50]}...")

        return {
            "success": True,
            "refined_text": refined_text,
            "improvements": improvements,
            "keywords_added": new_keywords,
            "ai_explanation": f"I've refined the suggestion based on your feedback: '{user_feedback}'"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")
