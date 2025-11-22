"""
Master Resume API Routes
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
from ...api.schemas.master_resume import (
    MasterResumeSchema,
    CreateMasterResumeRequest,
    BulletPointSchema,
    ExperienceSchema,
    EducationSchema,
    SkillSchema,
    PersonalInfoSchema
)
from ...domain.models import (
    MasterResume,
    Experience,
    BulletPoint,
    Education,
    Skill,
    PersonalInfo
)
from datetime import datetime

router = APIRouter(prefix="/master", tags=["Master Resume"])

# In-memory storage for MVP (replace with database in production)
master_resumes: Dict[str, MasterResume] = {}


@router.post("/resume")
async def create_master_resume(request: CreateMasterResumeRequest):
    """
    Create a new master resume

    This creates the master resume that contains all your experiences,
    projects, and skills. You'll use this to generate tailored resumes.

    Args:
        request: Master resume data

    Returns:
        Created master resume
    """
    try:
        # Convert request to domain model
        master = MasterResume(
            user_id="user_1",  # TODO: Get from auth
            personal_info=_schema_to_personal_info(request.personal_info),
            experiences=[_schema_to_experience(exp) for exp in request.experiences],
            education=[_schema_to_education(edu) for edu in request.education],
            skills=[_schema_to_skill(skill) for skill in request.skills],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Store in memory
        master_resumes[master.id] = master

        # Convert to schema and return with success flag
        return {
            "success": True,
            "master_resume": _master_to_schema(master)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create master resume: {str(e)}")


@router.get("/resume", response_model=MasterResumeSchema)
async def get_master_resume():
    """
    Get the user's master resume

    Returns:
        Master resume if exists, 404 otherwise
    """
    # For MVP, return the first (and only) master resume
    if not master_resumes:
        raise HTTPException(status_code=404, detail="No master resume found. Please create one first.")

    master_id = list(master_resumes.keys())[0]
    master = master_resumes[master_id]

    return _master_to_schema(master)


@router.put("/resume", response_model=MasterResumeSchema)
async def update_master_resume(request: CreateMasterResumeRequest):
    """
    Update master resume

    Args:
        request: Updated master resume data

    Returns:
        Updated master resume
    """
    # Get existing master
    if not master_resumes:
        raise HTTPException(status_code=404, detail="No master resume found")

    master_id = list(master_resumes.keys())[0]
    master = master_resumes[master_id]

    # Update fields
    master.personal_info = _schema_to_personal_info(request.personal_info)
    master.experiences = [_schema_to_experience(exp) for exp in request.experiences]
    master.education = [_schema_to_education(edu) for edu in request.education]
    master.skills = [_schema_to_skill(skill) for skill in request.skills]
    master.updated_at = datetime.now()

    return _master_to_schema(master)


# Helper functions to convert between schemas and domain models

def _schema_to_personal_info(schema: PersonalInfoSchema) -> PersonalInfo:
    if schema is None:
        return None
    return PersonalInfo(
        name=schema.name,
        email=schema.email,
        phone=schema.phone,
        linkedin=str(schema.linkedin) if schema.linkedin else None,
        github=str(schema.github) if schema.github else None
    )


def _schema_to_experience(schema: ExperienceSchema) -> Experience:
    return Experience(
        id=schema.id,
        company=schema.company,
        title=schema.title,
        location=schema.location,
        start_date=schema.start_date,
        end_date=schema.end_date,
        description=schema.description,
        bullets=[_schema_to_bullet(b) for b in schema.bullets],
        skills_used=schema.skills_used,
        industry=schema.industry
    )


def _schema_to_bullet(schema: BulletPointSchema) -> BulletPoint:
    return BulletPoint(
        id=schema.id,
        text=schema.text,
        keywords=schema.keywords,
        skills_used=schema.skills_used
    )


def _schema_to_education(schema: EducationSchema) -> Education:
    return Education(
        id=schema.id,
        school=schema.school,
        degree=schema.degree,
        start_date=schema.start_date,
        end_date=schema.end_date,
        description=schema.description
    )


def _schema_to_skill(schema: SkillSchema) -> Skill:
    return Skill(
        name=schema.name,
        category=schema.category
    )


def _master_to_schema(master: MasterResume) -> MasterResumeSchema:
    return MasterResumeSchema(
        id=master.id,
        user_id=master.user_id,
        personal_info=PersonalInfoSchema(
            name=master.personal_info.name if master.personal_info else None,
            email=master.personal_info.email if master.personal_info else None,
            phone=master.personal_info.phone if master.personal_info else None,
            linkedin=master.personal_info.linkedin if master.personal_info else None,
            github=master.personal_info.github if master.personal_info else None
        ) if master.personal_info else None,
        experiences=[
            ExperienceSchema(
                id=exp.id,
                company=exp.company,
                title=exp.title,
                location=exp.location,
                start_date=exp.start_date,
                end_date=exp.end_date,
                description=exp.description,
                bullets=[
                    BulletPointSchema(
                        id=b.id,
                        text=b.text,
                        keywords=b.keywords,
                        skills_used=b.skills_used
                    ) for b in exp.bullets
                ],
                skills_used=exp.skills_used,
                industry=exp.industry
            ) for exp in master.experiences
        ],
        education=[
            EducationSchema(
                id=edu.id,
                school=edu.school,
                degree=edu.degree,
                start_date=edu.start_date,
                end_date=edu.end_date,
                description=edu.description
            ) for edu in master.education
        ],
        skills=[
            SkillSchema(name=skill.name, category=skill.category)
            for skill in master.skills
        ],
        created_at=master.created_at,
        updated_at=master.updated_at
    )
