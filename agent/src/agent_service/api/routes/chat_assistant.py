"""AI Chat Assistant API Routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.use_cases.chat_assistant import ChatAssistantUseCase
from ...infra.llm.enhanced_llm import EnhancedLLMService
from ...infra.vector.simple_vector_store import SimpleVectorStore, get_vector_store
from ...infra.storage.database import get_db_session
from ..schemas.chat_schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    RelevantContext
)

router = APIRouter(prefix="/chat", tags=["AI Chat Assistant"])


# Dependency to get LLM service
def get_llm_service():
    """Get LLM service instance."""
    from ...config import get_settings
    settings = get_settings()
    return EnhancedLLMService(api_key=settings.openai_api_key)


# Dependency to get use case
async def get_chat_use_case(
    db: AsyncSession = Depends(get_db_session),
    llm_service: EnhancedLLMService = Depends(get_llm_service),
    vector_store: SimpleVectorStore = Depends(get_vector_store)
) -> ChatAssistantUseCase:
    """Get chat assistant use case with all dependencies."""
    return ChatAssistantUseCase(
        llm_service=llm_service,
        vector_store=vector_store,
        db_session=db
    )


@router.post(
    "/message",
    response_model=ChatMessageResponse,
    summary="Send Chat Message",
    description="""
    Send a message to the AI chat assistant and get optimization suggestions.

    **Features:**
    - Context-aware responses using resume data
    - RAG (Retrieval Augmented Generation) for relevant suggestions
    - Multi-turn conversation support
    - Retrieves relevant resume experiences for context

    **Returns:**
    - AI assistant's reply
    - Relevant resume experiences used for context
    - Chat session ID for continuing the conversation
    """
)
async def send_message(
    request: ChatMessageRequest,
    use_case: ChatAssistantUseCase = Depends(get_chat_use_case),
    user_id: str = "anonymous"  # TODO: Get from Clerk authentication
) -> ChatMessageResponse:
    """
    Send message to AI assistant.

    The assistant uses RAG to retrieve relevant experiences from your resume
    and provides personalized optimization suggestions.
    """
    try:
        result = await use_case.send_message(
            user_id=user_id,
            resume_version_id=request.resume_version_id,
            message=request.message,
            chat_session_id=request.chat_session_id
        )

        return ChatMessageResponse(
            session_id=result["session_id"],
            reply=result["reply"],
            relevant_context=[
                RelevantContext(**ctx) for ctx in result["relevant_context"]
            ]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post(
    "/index-resume",
    summary="Index Resume for Search",
    description="""
    Index resume content for vector search (RAG).

    This should be called after uploading a resume to enable
    context-aware chat responses.
    """
)
async def index_resume(
    resume_data: dict,
    use_case: ChatAssistantUseCase = Depends(get_chat_use_case),
    user_id: str = "anonymous"  # TODO: Get from Clerk authentication
):
    """
    Index resume content for vector search.

    This enables the chat assistant to retrieve relevant experiences
    when answering questions.
    """
    try:
        await use_case.index_resume_for_search(
            user_id=user_id,
            resume_data=resume_data
        )

        return {
            "status": "success",
            "message": "Resume indexed successfully for chat context"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume indexing failed: {str(e)}")
