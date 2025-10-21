from domain.models import Resume, ResumeSource, PersonalInfo, Experience, Education, Skill, ExperienceType
from api.schemas.build import BuildResumeRequest

class BuildResumeUseCase:
    def __init__(self, llm_service, retriever, template_engine):
        self.llm = llm_service
        self.retriever = retriever
        self.template = template_engine
    
    def execute(self, request: BuildResumeRequest) -> dict:
        """直接在这里转换"""
        
        # 1. Pydantic → Domain Model（很简单的转换）
        resume = Resume(
            source=ResumeSource.BUILT,
            personal_info=PersonalInfo(**request.personal_info.dict()),
            experiences=[
                Experience(
                    type=ExperienceType(exp.type),
                    **{k: v for k, v in exp.dict().items() if k != 'type'}
                )
                for exp in request.experiences
            ],
            education=[Education(**edu.dict()) for edu in request.education],
            skills=[Skill(name=s) for s in request.skills],
            summary=request.summary,
            target_job=request.target_job
        )
        
        # 2. 业务逻辑
        if request.enhance_with_ai:
            resume = self._enhance_resume(resume)
        
        # 3. 生成预览
        preview_html = self.template.render(resume)
        
        # 4. Domain Model → Dict（直接用 dataclasses.asdict）
        from dataclasses import asdict
        return {
            "resume": asdict(resume),
            "preview_html": preview_html
        }