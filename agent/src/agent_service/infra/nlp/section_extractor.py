"""Resume Section Extractor using LLM"""
import json
from typing import Dict
from ...domain.ports import LlmProviderPort
from ...domain.models import Resume, PersonalInfo, Experience, Education, Skill
from ...utils.text_clean import TextCleaner


class SectionExtractor:
    """Extract structured data from resume text using LLM"""

    def __init__(self, llm_provider: LlmProviderPort):
        """
        Initialize section extractor

        Args:
            llm_provider: LLM provider instance
        """
        self.llm = llm_provider
        self.text_cleaner = TextCleaner()

    async def extract_resume_data(self, text: str) -> Resume:
        """
        Extract structured resume data from text

        Args:
            text: Resume text content

        Returns:
            Resume object with extracted data
        """
        cleaned_text = self.text_cleaner.clean_text(text)

        system_prompt = """You are an expert resume parser. Extract structured information from the resume text.
Return a JSON object with the following structure:
{
  "personal_info": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "linkedin": "string",
    "github": "string"
  },
  "experiences": [
    {
      "company": "string",
      "title": "string",
      "location": "string",
      "start_date": "string",
      "end_date": "string",
      "description": "string"
    }
  ],
  "education": [
    {
      "school": "string",
      "degree": "string",
      "start_date": "string",
      "end_date": "string",
      "description": "string"
    }
  ],
  "skills": [
    {
      "name": "string",
      "category": "string"
    }
  ]
}

Extract all available information. Use null for missing fields. For descriptions, preserve the original bullet points."""

        user_prompt = f"Parse this resume and extract structured data:\n\n{cleaned_text}"

        try:
            response = await self.llm.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2000
            )

            # Parse JSON response
            data = json.loads(response)

            # Create Resume object
            resume = self._create_resume_from_json(data, text)
            return resume

        except json.JSONDecodeError:
            # Fallback: create basic resume with raw text
            return Resume(raw_text=cleaned_text)
        except Exception as e:
            raise RuntimeError(f"Failed to extract resume data: {str(e)}")

    def _create_resume_from_json(self, data: Dict, raw_text: str) -> Resume:
        """
        Create Resume object from JSON data

        Args:
            data: Parsed JSON data
            raw_text: Original resume text

        Returns:
            Resume object
        """
        # Extract personal info
        personal_info_data = data.get("personal_info", {})
        personal_info = PersonalInfo(
            name=personal_info_data.get("name"),
            email=personal_info_data.get("email"),
            phone=personal_info_data.get("phone"),
            linkedin=personal_info_data.get("linkedin"),
            github=personal_info_data.get("github")
        )

        # Extract experiences
        experiences = []
        for exp_data in data.get("experiences", []):
            exp = Experience(
                company=exp_data.get("company"),
                title=exp_data.get("title"),
                location=exp_data.get("location"),
                start_date=exp_data.get("start_date"),
                end_date=exp_data.get("end_date"),
                description=exp_data.get("description")
            )
            experiences.append(exp)

        # Extract education
        education = []
        for edu_data in data.get("education", []):
            edu = Education(
                school=edu_data.get("school"),
                degree=edu_data.get("degree"),
                start_date=edu_data.get("start_date"),
                end_date=edu_data.get("end_date"),
                description=edu_data.get("description")
            )
            education.append(edu)

        # Extract skills
        skills = []
        for skill_data in data.get("skills", []):
            skill = Skill(
                name=skill_data.get("name"),
                category=skill_data.get("category")
            )
            skills.append(skill)

        return Resume(
            personal_info=personal_info,
            experiences=experiences,
            education=education,
            skills=skills,
            raw_text=raw_text
        )
