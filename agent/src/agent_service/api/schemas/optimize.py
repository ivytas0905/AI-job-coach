from pydantic import BaseModel
from typing import List, Optional
from .resume import ParsedResumeSchema
from pydantic import Field

class OptimizeRequestSchema(BaseModel):
    """优化请求"""
    resume: ParsedResumeSchema
    #job_description: str

class OptimizeResponseSchema(BaseModel):
    """优化响应"""
    success: bool
    optimized_resume: Optional[ParsedResumeSchema] = None
    ats_score: Optional[int] = Field(None, ge=0, le=100)
    suggestions: List[str] = []
    error: Optional[str] = None