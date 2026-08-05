"""
AI-powered content enhancement endpoint
Enhances resume bullet points using LLM
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from ...application.ports.llm import LlmMessage, LlmProvider
from ...wiring import get_llm_provider

router = APIRouter(prefix="/resume", tags=["optimize"])

# ============= Request/Response Schema =============
class EnhanceRequest(BaseModel):
    """AI enhancement request"""
    description: str
    jobTitle: Optional[str] = None
    company: Optional[str] = None

class EnhanceSummaryRequest(BaseModel):
    """AI enhancement request for summary"""
    summary: str
    targetJob: Optional[str] = None
    skills: Optional[List[str]] = None
    yearsOfExperience: Optional[int] = None

class EnhanceResponse(BaseModel):
    """AI enhancement response"""
    success: bool
    enhanced: str

# ============= API Endpoint =============
@router.post("/enhance",response_model = EnhanceResponse)
          
# 完整路径：/api/resume/enhance
async def enhance_content(
    request: EnhanceRequest,
    llm: LlmProvider = Depends(get_llm_provider),
):
    """
    Enhance work experience description using AI
    
    POST /api/resume/enhance
    
    Body:
    {
        "description": "worked on projects",
        "jobTitle": "Software Engineer",
        "company": "Google"
    }
    
    Returns:
    {
        "success": true,
        "enhanced": "• Developed and deployed..."
    }
    """
    try:
        # 1. 验证输入
        if not request.description or not request.description.strip():
            raise HTTPException(
                status_code=400,
                detail="Description is required"
            )
        
        # 2. 构建提示词
        prompt = _build_enhancement_prompt(
            description=request.description,
            job_title=request.jobTitle,
            company=request.company
        )
        
        # 3. 调用 LLM
        result = await llm.complete(
            [LlmMessage(role="user", content=prompt)],
            max_tokens=1500,
            temperature=0.7
        )
        enhanced_text = result.text or ""
        
        # 4. 返回结果
        return EnhanceResponse(
            success=True,
            enhanced=enhanced_text.strip()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Enhancement error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enhance: {str(e)}"
        )



#=====summary enhance part=====#
@router.post("/enhance-summary",response_model = EnhanceResponse)
async def enhance_summary(
    request: EnhanceSummaryRequest,
    llm_provider: LlmProvider = Depends(get_llm_provider),
):
    """
    Enhance professional summary using AI
    
    POST /api/resume/enhance-summary
    
    Request body:
    {
        "summary": "I am a software engineer with experience",
        "targetJob": "Senior Software Engineer",
        "skills": ["Python", "React", "AWS"],
        "yearsOfExperience": 5
    }
    
    Response:
    {
        "success": true,
        "enhanced": "Results-driven Senior Software Engineer with 5+ years..."
    }
    """
    try:
        if not request.summary or not request.summary.strip():
            raise HTTPException(
                status_code=400,
                detail="Summary is required"
            )
        
        prompt = _build_summary_prompt(
            summary=request.summary,
            target_job=request.targetJob,
            skills=request.skills,
        )
        
        result = await llm_provider.complete(
            [LlmMessage(role="user", content=prompt)],
            max_tokens=800,  # Summary is shorter
            temperature=0.6
        )
        enhanced_text = result.text or ""
        
        return EnhanceResponse(
            success=True,
            enhanced=enhanced_text.strip()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Summary enhancement error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enhance summary: {str(e)}"
        )


# ============= Helper Functions =============
def _build_enhancement_prompt(
    description: str,
    job_title: Optional[str] = None,
    company: Optional[str] = None
) -> str:
    """Build enhancement prompt for experience (已有)"""
    
    context_parts = []
    if job_title:
        context_parts.append(f"Position: {job_title}")
    if company:
        context_parts.append(f"Company: {company}")
    
    context = "\n".join(context_parts) if context_parts else ""
    
    prompt = f"""You are a professional resume optimization expert. Enhance the following work experience description to make it more professional and impactful.

{context}

Original Description:
{description}

Enhancement Requirements:
1. Start with strong action verbs (Developed, Designed, Implemented, Optimized, Led, Increased)
2. Preserve factual accuracy; never invent numbers, percentages, or timeframes
3. Highlight technical skills and business value
4. Use bullet points (start with •)
5. Keep each point concise (1-2 lines)
6. Maintain a professional tone
7. Focus on impact and results

Return ONLY the enhanced description with bullet points (•), one achievement per line. Do not add any explanations or extra content."""

    return prompt


def _build_summary_prompt(
    summary: str,
    target_job: Optional[str] = None,
    skills: Optional[List[str]] = None,
    
) -> str:
    """Build enhancement prompt for summary (新增) ⭐"""
    
    # 构建上下文信息
    context_parts = []
    if target_job:
        context_parts.append(f"Target Position: {target_job}")
    
    if skills:
        context_parts.append(f"Key Skills: {', '.join(skills[:5])}")  # 只取前5个技能
    
    context = "\n".join(context_parts) if context_parts else ""
    
    prompt = f"""You are a professional resume writer. Enhance the following professional summary to make it compelling and impactful.

{context}

Original Summary:
{summary}

Enhancement Requirements:
1. Start with a strong opening that highlights the candidate's value proposition
2. Include years of experience if provided
3. Mention key technical skills naturally
4. Emphasize achievements and impact
5. Keep it concise: 3-4 sentences maximum
6. Use action-oriented language
7. Tailor to the target position if provided
8. Write in third person without using pronouns (avoid "I", "my")
9. Make it ATS-friendly by including relevant keywords

Return ONLY the enhanced summary as a single paragraph. Do not add any explanations, headers, or extra content."""

    return prompt
