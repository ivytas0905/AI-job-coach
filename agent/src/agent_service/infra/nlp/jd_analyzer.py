"""
Job Description Analyzer using LLM
"""
from typing import List
from ...domain.models import JobDescription, KeywordWeight
from ...domain.ports import LlmProviderPort
import json
import re


class JDAnalyzer:
    """Analyzes job descriptions to extract structured information"""

    def __init__(self, llm_provider: LlmProviderPort):
        self.llm = llm_provider

    async def analyze(self, raw_text: str) -> JobDescription:
        """
        Analyze job description and extract structured information

        Args:
            raw_text: Raw job description text

        Returns:
            JobDescription with extracted information
        """
        # Extract basic info using LLM
        analysis_result = await self._extract_structured_data(raw_text)

        # Create JD object
        jd = JobDescription(
            raw_text=raw_text,
            company=analysis_result.get("company"),
            position=analysis_result.get("position"),
            required_skills=analysis_result.get("required_skills", []),
            preferred_skills=analysis_result.get("preferred_skills", []),
            responsibilities=analysis_result.get("responsibilities", []),
            qualifications=analysis_result.get("qualifications", []),
            industry=analysis_result.get("industry"),
            keywords=self._create_weighted_keywords(analysis_result)
        )

        return jd

    async def _extract_structured_data(self, raw_text: str) -> dict:
        """
        Use LLM to extract structured data from JD
        """
        system_prompt = """You are an expert at analyzing job descriptions.
Extract key information and return it in JSON format."""

        prompt = f"""Analyze this job description and extract the following information in JSON format:

Job Description:
{raw_text}

CRITICAL INSTRUCTIONS:
1. required_skills and preferred_skills = ONLY technical/professional skills (e.g., Python, AWS, Leadership, SQL)
2. keywords = ONLY action verbs and important nouns from responsibilities (e.g., "develop", "design", "architecture", "scalability")
3. NO OVERLAP between skills and keywords

Return JSON:
{{
    "company": "Company name (if mentioned)",
    "position": "Job title",
    "industry": "Industry (e.g., Tech, Finance, Healthcare)",
    "required_skills": ["Python", "AWS", "Docker"],  // SKILLS ONLY
    "preferred_skills": ["Kubernetes", "GraphQL"],  // SKILLS ONLY
    "responsibilities": ["resp1", "resp2"],
    "qualifications": ["qual1", "qual2"],
    "keywords": [
        {{"text": "develop", "weight": 0.9, "category": "required"}},
        {{"text": "architecture", "weight": 0.8, "category": "required"}},
        {{"text": "optimize", "weight": 0.7, "category": "preferred"}}
    ]  // ACTION VERBS + KEY NOUNS ONLY, NO SKILLS
}}

Keyword extraction rules:
- Extract ACTION VERBS: develop, design, lead, implement, optimize, manage, build, architect, collaborate, mentor
- Extract KEY NOUNS: architecture, scalability, performance, security, automation, infrastructure, pipelines
- Weight: 0.9-1.0 for most critical, 0.7-0.8 for important, 0.5-0.6 for secondary
- Limit to 10-15 most important keywords

Return ONLY valid JSON, no markdown formatting."""

        try:
            response = await self.llm.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Low temperature for consistent extraction
                max_tokens=2000
            )

            # Parse JSON response
            # Remove markdown code blocks if present
            json_text = re.sub(r'```json\s*|\s*```', '', response).strip()
            result = json.loads(json_text)

            return result

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from LLM response: {e}")
            print(f"Response was: {response}")
            # Return minimal structure on error
            return {
                "company": None,
                "position": self._extract_position_fallback(raw_text),
                "industry": None,
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": [],
                "qualifications": [],
                "keywords": []
            }
        except Exception as e:
            print(f"Error in JD analysis: {e}")
            raise

    def _create_weighted_keywords(self, analysis_result: dict) -> List[KeywordWeight]:
        """
        Create KeywordWeight objects from analysis result
        """
        keywords = []

        # Add keywords from analysis
        for kw_data in analysis_result.get("keywords", []):
            keywords.append(KeywordWeight(
                text=kw_data["text"],
                weight=kw_data["weight"],
                category=kw_data["category"]
            ))

        return keywords

    def _extract_position_fallback(self, text: str) -> str:
        """
        Fallback method to extract position from text
        """
        # Look for common position patterns
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) < 100:  # Likely a title
                # Remove common prefixes
                line = re.sub(r'^(position:|role:|job title:)\s*', '', line, flags=re.IGNORECASE)
                if line:
                    return line

        return "Unknown Position"
