from fastapi import APIRouter, HTTPException, Depends
from src.agent_service.api.schemas.build import BuildResumeRequest, BuildResumeResponse
from application.use_cases.build_resume import BuildResumeUseCase
from infra.llm.togetherai_provider import TogetherProvider



