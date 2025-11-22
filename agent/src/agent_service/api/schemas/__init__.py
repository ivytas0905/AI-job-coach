<<<<<<< HEAD
from .optimize import OptimizeRequest, OptimizeResponse
from .resume import (ParsedResumeSchema,
    PersonalInfoSchema,
    ExperienceSchema,
    EducationSchema,
    SkillSchema
)


__all__ = ["ParsedResume",
    "ParsedResumeSchema",
    "PersonalInfoSchema",
    "ExperienceSchema",
    "EducationSchema",
    "SkillSchema",
    "AtsScore",
    "SectionSuggestion",
    "OptimizeResponse",
    "OptimizeRequest"
=======
from .optimize import OptimizeRequestSchema, OptimizeResponseSchema
from .resume import ParsedResumeSchema
from .master_resume import (
    MasterResumeSchema,
    CreateMasterResumeRequest,
    UpdateMasterResumeRequest,
    AddExperienceRequest,
    UpdateExperienceRequest,
    AddBulletPointRequest,
    UpdateBulletPointRequest,
    BulletPointSchema,
    ExperienceSchema
)
from .job_description import (
    JobDescriptionSchema,
    AnalyzeJDRequest,
    AnalyzeJDResponse,
    KeywordWeightSchema
)
from .tailored_resume import (
    TailoredResumeSchema,
    TailorResumeRequest,
    TailorResumeResponse,
    BulletOptimizationSchema,
    UpdateBulletStatusRequest,
    ApplyOptimizationsRequest
)


__all__ = [
    # Phase 1
    "ParsedResumeSchema",
    "OptimizeRequestSchema",
<<<<<<< HEAD
    "OptimizeResponseSchema"
>>>>>>> origin/feature/backend-infrastructure
=======
    "OptimizeResponseSchema",
    # Master Resume
    "MasterResumeSchema",
    "CreateMasterResumeRequest",
    "UpdateMasterResumeRequest",
    "AddExperienceRequest",
    "UpdateExperienceRequest",
    "AddBulletPointRequest",
    "UpdateBulletPointRequest",
    "BulletPointSchema",
    "ExperienceSchema",
    # Job Description
    "JobDescriptionSchema",
    "AnalyzeJDRequest",
    "AnalyzeJDResponse",
    "KeywordWeightSchema",
    # Tailored Resume
    "TailoredResumeSchema",
    "TailorResumeRequest",
    "TailorResumeResponse",
    "BulletOptimizationSchema",
    "UpdateBulletStatusRequest",
    "ApplyOptimizationsRequest"
>>>>>>> origin/feature/api-routes-and-frontend
]
