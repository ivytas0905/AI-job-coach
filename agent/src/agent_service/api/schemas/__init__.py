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
]
