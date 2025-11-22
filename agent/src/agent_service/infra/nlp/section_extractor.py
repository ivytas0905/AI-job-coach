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

CRITICAL: For experience descriptions, PRESERVE EACH BULLET POINT AS A SEPARATE STRING in an array.

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
      "bullets": [
        "First bullet point text",
        "Second bullet point text",
        "Third bullet point text"
      ]
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

IMPORTANT RULES:
- Each bullet point should be a SEPARATE string in the "bullets" array
- Remove bullet point symbols (•, -, *, etc.) from the text
- Keep the original wording exactly as written
- Extract all available information
- Use null for missing fields"""

        user_prompt = f"Parse this resume and extract structured data:\n\n{cleaned_text}"

        try:
            response = await self.llm.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.1,  # Lower temperature for faster, more consistent results
                max_tokens=1500  # Reduced tokens for faster response
            )

            print(f"[DEBUG] LLM Response: {response[:500]}...")  # Print first 500 chars

            # Remove markdown code blocks if present
            cleaned_response = response.strip()
            if cleaned_response.startswith('```'):
                # Remove ```json or ``` from start
                cleaned_response = cleaned_response.split('\n', 1)[1] if '\n' in cleaned_response else cleaned_response[3:]
            if cleaned_response.endswith('```'):
                # Remove ``` from end
                cleaned_response = cleaned_response.rsplit('\n```', 1)[0]

            cleaned_response = cleaned_response.strip()

            # Parse JSON response
            data = json.loads(cleaned_response)
            print(f"[DEBUG] Parsed data keys: {data.keys()}")
            print(f"[DEBUG] Has experiences: {len(data.get('experiences', []))}")
            print(f"[DEBUG] Has education: {len(data.get('education', []))}")
            print(f"[DEBUG] Has skills: {len(data.get('skills', []))}")

            # Create Resume object
            resume = self._create_resume_from_json(data, text)
            return resume

        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decode error: {e}")
            print(f"[ERROR] Response was: {response}")
            # Fallback: create basic resume with raw text
            return Resume(raw_text=cleaned_text)
        except Exception as e:
            print(f"[ERROR] Exception in extract_resume_data: {e}")
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
            # Handle both new format (bullets) and old format (description)
            bullets_data = exp_data.get("bullets", [])
            if not bullets_data and exp_data.get("description"):
                # Fallback: split description into bullets if bullets not provided
                bullets_data = [exp_data.get("description")]

            # Join bullets with newlines for description field
            description = "\n".join(bullets_data) if bullets_data else None

            exp = Experience(
                company=exp_data.get("company"),
                title=exp_data.get("title"),
                location=exp_data.get("location"),
                start_date=exp_data.get("start_date"),
                end_date=exp_data.get("end_date"),
                description=description
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
