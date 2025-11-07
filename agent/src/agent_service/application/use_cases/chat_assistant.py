"""
AI Chat Assistant Use Case with RAG

Provides intelligent resume optimization suggestions through conversational AI.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from ...infra.llm.enhanced_llm import EnhancedLLMService
from ...infra.vector.simple_vector_store import SimpleVectorStore
from ...infra.storage.models import ChatSessionModel, ResumeVersionModel


class ChatAssistantUseCase:
    """
    AI Chat Assistant for resume optimization.

    Features:
    - Context-aware responses using resume data
    - RAG (Retrieval Augmented Generation) for relevant suggestions
    - Chat history management
    """

    def __init__(
        self,
        llm_service: EnhancedLLMService,
        vector_store: SimpleVectorStore,
        db_session: AsyncSession
    ):
        self.llm = llm_service
        self.vector_store = vector_store
        self.db = db_session

    async def send_message(
        self,
        user_id: str,
        resume_version_id: str,
        message: str,
        chat_session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send message to AI assistant and get response.

        Args:
            user_id: User ID
            resume_version_id: Resume version for context
            message: User's message
            chat_session_id: Existing chat session ID (or None for new session)

        Returns:
            {
                "session_id": str,
                "reply": str,
                "relevant_context": List[dict]
            }
        """
        # Get or create chat session
        if chat_session_id:
            session = await self._get_session(chat_session_id)
        else:
            session = await self._create_session(user_id, resume_version_id)

        # Get resume context
        resume_context = await self._get_resume_context(resume_version_id)

        # Get relevant experiences using vector search
        relevant_context = await self._search_relevant_context(
            user_id=user_id,
            query=message,
            top_k=3
        )

        # Build context string
        context_str = self._build_context_string(resume_context, relevant_context)

        # Get chat history
        chat_history = session.messages if isinstance(session.messages, list) else []

        # Generate response
        reply = await self.llm.generate_chat_response(
            user_message=message,
            context=context_str,
            chat_history=chat_history
        )

        # Update chat history
        chat_history.append({"role": "user", "content": message, "timestamp": datetime.utcnow().isoformat()})
        chat_history.append({"role": "assistant", "content": reply, "timestamp": datetime.utcnow().isoformat()})

        session.messages = chat_history
        session.last_activity_at = datetime.utcnow()

        await self.db.commit()

        return {
            "session_id": session.id,
            "reply": reply,
            "relevant_context": relevant_context
        }

    async def index_resume_for_search(
        self,
        user_id: str,
        resume_data: Dict[str, Any]
    ):
        """
        Index resume content for vector search.

        Args:
            user_id: User ID
            resume_data: Parsed resume data
        """
        entries = []

        # Index work experiences
        for exp_idx, exp in enumerate(resume_data.get('experience', [])):
            for bullet_idx, bullet in enumerate(exp.get('bullet_points', [])):
                # Generate embedding
                embedding = await self.llm.embed_text(
                    f"{exp.get('company', '')} - {exp.get('title', '')}: {bullet}"
                )

                entries.append({
                    'id': f"{user_id}_exp_{exp_idx}_{bullet_idx}",
                    'vector': embedding,
                    'payload': {
                        'user_id': user_id,
                        'type': 'experience',
                        'content': bullet,
                        'company': exp.get('company', ''),
                        'title': exp.get('title', '')
                    }
                })

        # Batch add to vector store
        if entries:
            self.vector_store.add_vectors_batch(entries)
            print(f"✓ Indexed {len(entries)} resume items for user {user_id}")

    async def _search_relevant_context(
        self,
        user_id: str,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Search for relevant resume content."""
        # Generate query embedding
        query_embedding = await self.llm.embed_text(query)

        # Search vector store
        results = self.vector_store.search(
            query_vector=query_embedding,
            top_k=top_k,
            filter_payload={"user_id": user_id}
        )

        return [
            {
                "content": result["payload"]["content"],
                "company": result["payload"].get("company", ""),
                "score": result["score"]
            }
            for result in results
        ]

    async def _get_session(self, session_id: str) -> ChatSessionModel:
        """Get existing chat session."""
        stmt = select(ChatSessionModel).where(ChatSessionModel.id == session_id)
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if session is None:
            raise ValueError(f"Chat session {session_id} not found")

        return session

    async def _create_session(
        self,
        user_id: str,
        resume_version_id: str
    ) -> ChatSessionModel:
        """Create new chat session."""
        session = ChatSessionModel(
            user_id=user_id,
            resume_version_id=resume_version_id,
            messages=[],
            created_at=datetime.utcnow()
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def _get_resume_context(self, resume_version_id: str) -> Dict[str, Any]:
        """Get resume version for context."""
        stmt = select(ResumeVersionModel).where(ResumeVersionModel.id == resume_version_id)
        result = await self.db.execute(stmt)
        resume = result.scalar_one_or_none()

        if resume is None:
            return {}

        return {
            "job_title": resume.job_title or "Not specified",
            "company": resume.company or "Not specified",
            "target_keywords": resume.target_keywords or []
        }

    def _build_context_string(
        self,
        resume_context: Dict[str, Any],
        relevant_experiences: List[Dict[str, Any]]
    ) -> str:
        """Build context string for LLM."""
        context_parts = [
            "RESUME CONTEXT:",
            f"- Target Job: {resume_context.get('job_title', 'N/A')}",
            f"- Target Company: {resume_context.get('company', 'N/A')}",
            f"- Target Keywords: {', '.join(resume_context.get('target_keywords', [])[:5])}"
        ]

        if relevant_experiences:
            context_parts.append("\nRELEVANT EXPERIENCES:")
            for exp in relevant_experiences:
                context_parts.append(f"- [{exp['company']}] {exp['content']}")

        return "\n".join(context_parts)
