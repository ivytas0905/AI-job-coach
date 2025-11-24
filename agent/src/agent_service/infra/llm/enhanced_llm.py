"""Enhanced LLM Service - Extended capabilities for resume optimization"""

from typing import List, Dict, Any, Optional
import json
import re
from .llm_manager import LLMManager
from ...config import get_settings
from ..knowledge import get_knowledge_base


class EnhancedLLMService:
    """
    Enhanced LLM Service with specialized methods for resume optimization.

    This extends the basic OpenAI provider with domain-specific capabilities:
    - JD analysis and keyword extraction
    - STAR-framework bullet point optimization
    - Text embeddings for RAG
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize enhanced LLM service.

        Args:
            api_key: OpenAI API key (defaults to settings)
        """
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        # Use LLM Manager with automatic fallback support
        self.llm_manager = LLMManager()
        self.embedding_model = "text-embedding-3-small"

    async def analyze_jd(
        self,
        jd_text: str,
        job_title: str
    ) -> Dict[str, Any]:
        """
        Analyze job description and extract key information.

        This uses GPT-4o-mini with structured output to extract:
        - TOP 20 keywords with weights and types
        - Required vs preferred skills
        - Common action verbs
        - Industry/domain keywords

        Args:
            jd_text: Raw job description text
            job_title: Job title for context

        Returns:
            Dictionary with analysis results:
            {
                "top_keywords": [
                    {"keyword": str, "weight": float, "type": str},
                    ...
                ],
                "required_skills": [str, ...],
                "preferred_skills": [str, ...],
                "common_verbs": [str, ...],
                "common_nouns": [str, ...],
                "industry": str
            }
        """
        system_prompt = """You are an expert resume optimization assistant specializing in ATS (Applicant Tracking System) optimization.

Your task is to analyze job descriptions and extract the most important keywords that should appear in a resume to pass ATS screening."""

        user_prompt = f"""Analyze the following job description and extract key information in a structured way.

Job Title: {job_title}

Job Description:
{jd_text}

Please provide a JSON response with the following structure:
{{
  "sections": {{
    "summary": "Brief company/role summary text (if exists)",
    "description": "Main job description text (if exists)",
    "responsibilities": ["Responsibility 1", "Responsibility 2", ...],
    "minimum_qualifications": ["Qualification 1", "Qualification 2", ...],
    "preferred_qualifications": ["Preferred 1", "Preferred 2", ...],
    "benefits": ["Benefit 1", "Benefit 2", ...] (if mentioned)
  }},
  "top_keywords": [
    {{"keyword": "Python", "weight": 0.95, "type": "technical_skill"}},
    {{"keyword": "Machine Learning", "weight": 0.90, "type": "technical_skill"}},
    ...
    // Include TOP 20 keywords sorted by importance
  ],
  "required_skills": ["skill1", "skill2", ...],
  "preferred_skills": ["skill1", "skill2", ...],
  "common_verbs": ["developed", "implemented", ...],
  "common_nouns": ["system", "model", ...],
  "industry": "technology|finance|healthcare|etc"
}}

Guidelines:
1. **Section Identification**: Intelligently identify different sections in the JD:
   - Look for headers like "About", "Summary", "Description", "Overview"
   - Look for "Responsibilities", "What you'll do", "Key Responsibilities"
   - Look for "Requirements", "Qualifications", "Must have", "Minimum Qualifications"
   - Look for "Preferred", "Nice to have", "Preferred Qualifications", "Bonus"
   - Look for "Benefits", "What we offer", "Perks"

2. **Keyword extraction**:
   - Weight should be 0.0 to 1.0 (1.0 = most important)
   - Type should be: technical_skill, soft_skill, tool, certification, or domain_knowledge
   - Prioritize keywords that appear multiple times or in critical sections (requirements, qualifications)
   - Include both exact phrases and variations (e.g., "ML" and "Machine Learning")
   - Extract TOP 20 most important keywords

3. **Skills categorization**:
   - required_skills: From "Minimum Qualifications", "Requirements", "Must have"
   - preferred_skills: From "Preferred Qualifications", "Nice to have", "Bonus"

Only return valid JSON, no additional text."""

        try:
            # Use LLM Manager (with automatic fallback)
            response = await self.llm_manager.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for consistent extraction
                max_tokens=2000
            )

            # Parse JSON response
            analysis = json.loads(response)

            # Validate and ensure we have top 20 keywords
            if "top_keywords" not in analysis:
                analysis["top_keywords"] = []

            # Sort by weight and take top 20
            analysis["top_keywords"] = sorted(
                analysis["top_keywords"],
                key=lambda x: x.get("weight", 0),
                reverse=True
            )[:20]

            return analysis

        except json.JSONDecodeError as e:
            # Fallback: try to extract keywords using basic NLP if JSON parsing fails
            print(f"JSON parsing failed, using fallback: {e}")
            return self._fallback_jd_analysis(jd_text, job_title)

        except Exception as e:
            raise RuntimeError(f"JD analysis failed: {str(e)}")

    def _fallback_jd_analysis(self, jd_text: str, job_title: str) -> Dict[str, Any]:
        """Fallback method for JD analysis if LLM fails."""
        # Simple keyword extraction as fallback
        words = re.findall(r'\b[A-Z][a-z]+\b|\b[A-Z]+\b', jd_text)
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only words longer than 3 characters
                word_freq[word] = word_freq.get(word, 0) + 1

        # Get top keywords
        top_keywords = [
            {
                "keyword": word,
                "weight": min(count / 10, 1.0),
                "type": "general"
            }
            for word, count in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        ]

        return {
            "top_keywords": top_keywords,
            "required_skills": [],
            "preferred_skills": [],
            "common_verbs": [],
            "common_nouns": [],
            "industry": "unknown"
        }

    async def optimize_bullet_star(
        self,
        bullet: str,
        target_keywords: List[str],
        context: Dict[str, Any],
        used_verbs: List[str] = None
    ) -> str:
        """
        Optimize a resume bullet point using the STAR framework.

        STAR = Situation, Task, Action, Result

        Args:
            bullet: Original bullet point text
            target_keywords: Keywords to incorporate
            context: Additional context (company, title, job_title)

        Returns:
            Optimized bullet point text
        """
        # Get knowledge base context
        kb = get_knowledge_base()
        kb_context = kb.build_optimization_context()
        anti_hallucination_principles = kb.get_anti_hallucination_principles()

        system_prompt = f"""You are an expert resume writer specializing in ATS-optimized, achievement-focused bullet points.

Your expertise:
1. STAR Framework (Situation, Task, Action, Result)
2. Strong action verbs
3. Quantifiable metrics
4. ATS keyword optimization
5. Concise, impactful writing (1-2 lines)

{kb_context}

CRITICAL ANTI-HALLUCINATION RULES:
{chr(10).join('- ' + principle for principle in anti_hallucination_principles)}

REMEMBER:
- ONLY use information from the original bullet
- NEVER invent numbers, technologies, or achievements
- If information is missing, keep it general or suggest where to add details
- Base ALL optimizations on user-provided facts"""

        # Extract context
        company = context.get('company', '')
        title = context.get('title', '')
        job_title = context.get('job_title', '')

        # Build used verbs warning
        if used_verbs is None:
            used_verbs = []
        verbs_warning = ""
        if used_verbs:
            verbs_warning = f"\n🚫 ALREADY USED VERBS (DO NOT REPEAT): {', '.join(used_verbs)}\nYou MUST use a DIFFERENT verb!\n"

        user_prompt = f"""Optimize the following resume bullet point.

ORIGINAL BULLET:
{bullet}

CONTEXT:
- Company: {company}
- Your Role: {title}
- Target Job: {job_title}
{verbs_warning}
TARGET KEYWORDS (REFERENCE ONLY):
{', '.join(target_keywords[:5])}

⚠️ CRITICAL ANTI-HALLUCINATION RULES:
1. ONLY use information explicitly stated in the ORIGINAL BULLET
2. NEVER add technologies, features, or achievements not mentioned in the original
3. NEVER add keywords if they don't accurately describe what's in the original bullet
4. If a keyword doesn't match the original content, SKIP IT - don't force it
5. DO NOT invent metrics, numbers, or capabilities

REQUIREMENTS:

1. **Choose the RIGHT action verb** based on contribution type:
   {f"🚫 NEVER USE THESE (already used): {', '.join(used_verbs)}" if used_verbs else ""}

   For INNOVATION/CREATION: Pioneered, Architected, Engineered, Designed, Conceived, Developed, Built, Created, Generated, Invented

   For LEADERSHIP/INITIATIVE: Led, Directed, Orchestrated, Championed, Drove, Steered, Guided, Helmed, Commanded, Mobilized

   For EXECUTION/DELIVERY: Implemented, Deployed, Executed, Launched, Delivered, Established, Introduced, Rolled out, Operationalized

   For IMPROVEMENT/OPTIMIZATION: Enhanced, Streamlined, Refined, Transformed, Modernized, Revitalized, Upgraded, Strengthened, Accelerated, Boosted

   For ANALYSIS/RESEARCH: Analyzed, Investigated, Evaluated, Assessed, Researched, Examined, Measured, Quantified, Studied

   For COLLABORATION/FACILITATION: Facilitated, Collaborated, Coordinated, Partnered, Enabled, Unified, Integrated, Aligned, Synchronized

   For TECHNICAL WORK: Built, Coded, Programmed, Configured, Automated, Integrated, Debugged, Migrated, Refactored

   **CRITICAL: You MUST use a verb that is NOT in the "already used" list above!**

2. Apply STAR framework:
   - Situation/Task: Brief context (optional, integrate naturally)
   - Action: What you did - use the MOST ACCURATE verb
   - Result: Quantifiable impact with numbers

3. **Keyword Usage - STRICT RULES**:
   - ONLY add a keyword if it accurately describes something ALREADY in the original bullet
   - If the original mentions "React.js", you can add "React" keyword
   - If the original mentions "GPT-4 API", you can add "AI" or "LLM" keyword
   - If the original does NOT mention video/image/processing, DO NOT add those keywords
   - Better to skip keywords than to fabricate content

4. Keep ALL numbers and metrics from the original:
   - If original says "140 students", keep "140 students"
   - If original says "GPT-4 API", keep "GPT-4 API"
   - DO NOT change or invent numbers

5. Keep it concise and impactful (1-2 lines max)

6. Match the technical level to the original bullet - don't oversell

EXAMPLE:
Original: "Built teaching platform using React.js for students"
Target Keywords: ["Python", "video processing", "AI"]
❌ WRONG: "Built AI-powered teaching platform using Python for video processing" (invented features!)
✅ CORRECT: "Engineered teaching platform using React.js serving students with AI-enhanced features" (only added "AI" because it's general enough)

OUTPUT:
Return ONLY the optimized bullet point text, no explanations."""

        try:
            optimized = await self.llm_manager.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,  # Some creativity for natural language
                max_tokens=200
            )

            # Clean up response
            optimized = optimized.strip()
            # Remove bullet points or dashes if LLM added them
            optimized = re.sub(r'^[-•*]\s*', '', optimized)

            return optimized

        except Exception as e:
            raise RuntimeError(f"Bullet optimization failed: {str(e)}")

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate text embedding vector using OpenAI embeddings.

        This is used for RAG (Retrieval Augmented Generation) to find
        similar resume experiences or job descriptions.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (list of floats, dimension 1536)
        """
        try:
            # Use OpenAI embeddings API
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)

            response = await client.embeddings.create(
                model=self.embedding_model,
                input=text
            )

            return response.data[0].embedding

        except Exception as e:
            raise RuntimeError(f"Text embedding failed: {str(e)}")

    async def batch_embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Batch embed multiple texts for efficiency.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)

            # OpenAI supports batch embedding
            response = await client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )

            # Return embeddings in the same order as input
            return [item.embedding for item in response.data]

        except Exception as e:
            raise RuntimeError(f"Batch embedding failed: {str(e)}")

    async def generate_chat_response(
        self,
        user_message: str,
        context: str,
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Generate AI chat response with resume optimization context.

        Args:
            user_message: User's question/request
            context: Resume context (relevant experiences, keywords, etc.)
            chat_history: Previous messages for continuity

        Returns:
            AI assistant response
        """
        system_prompt = f"""You are a professional resume optimization assistant with expertise in:
- ATS optimization
- STAR framework
- Keyword optimization
- Career coaching

CONTEXT:
{context}

Provide specific, actionable advice. Be concise and professional."""

        # Build conversation history
        conversation = []
        if chat_history:
            for msg in chat_history[-5:]:  # Last 5 messages for context
                conversation.append(msg)

        conversation.append({
            "role": "user",
            "content": user_message
        })

        # For now, use simple generation (can be enhanced with multi-turn support)
        full_prompt = f"{context}\n\nUser: {user_message}\n\nAssistant:"

        try:
            response = await self.llm_manager.generate_text(
                prompt=full_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=500
            )

            return response

        except Exception as e:
            raise RuntimeError(f"Chat response generation failed: {str(e)}")
