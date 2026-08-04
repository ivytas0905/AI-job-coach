from ...domain.models import Resume, ResumeSource, PersonalInfo, Experience, Education, Skill, ExperienceType
from ...api.schemas.build import BuildResumeRequest

class BuildResumeUseCase:
    def __init__(self, llm_service, retriever, template_engine):
        self.llm = llm_service
        self.retriever = retriever
        self.template = template_engine
    
    # def execute(self, request: BuildResumeRequest) -> dict:
    #     """直接在这里转换"""
        
    #     # 1. Pydantic → Domain Model
    #     resume = Resume(
    #         #source=ResumeSource.BUILT,
    #         personal_info=PersonalInfo(**request.contact.dict()),
    #         experiences=[
    #             Experience(
    #                 type=ExperienceType(exp.type),
    #                 **{k: v for k, v in exp.dict().items() if k != 'type'}
    #             )
    #             for exp in request.experiences
    #         ],
    #         education=[Education(**edu.dict()) for edu in request.education],
    #         skills=[Skill(name=s) for s in request.skills],
    #         summary=request.summary,
    #         target_job=request.target_job
    #     )
        
    #     # 2. 业务逻辑
    #     if request.enhance_with_ai:
    #         resume = self._enhance_resume(resume)
        
    #     # 3. 生成预览
    #     preview_html = self.template.render(resume)
        
    #     # 4. Domain Model → Dict（直接用 dataclasses.asdict）
    #     from dataclasses import asdict
    #     return {
    #         "resume": asdict(resume),
    #         "preview_html": preview_html
    #     }

    def execute(self, request: BuildResumeRequest) -> dict:
        
        resume = Resume(
        # source=ResumeSource.BUILT,  
        personal_info=PersonalInfo(
            
            fullname=request.contact.fullName,
            email=request.contact.email,
            phone=request.contact.phone,
            location=request.contact.location,
            title=request.contact.title
        ),
        experiences=[
            Experience(
                type=exp.position if hasattr(exp, 'type') else "WORK",  # 如果没有 type 就用默认值
                title=exp.position,
                company=exp.company,
                location=exp.location,
                start_date=exp.startDate,
                end_date=exp.endDate,
                description=exp.description
            )
            for exp in request.experience  # 改成 experience
        ],
        education=[
            Education(
                degree=edu.degree,
                school=edu.school,
                start_date=edu.startDate,
                end_date=edu.endDate,
                location=edu.location
            ) 
            for edu in request.education
        ],
        skills=[Skill(name=s) for s in request.skills],
        summary=request.summary,
        target_job=request.targetJob
    )
    
    # 2. 业务逻辑
        if request.enhanceWithAI:  # 
            resume = self._enhance_resume(resume)
    
    # 3. 生成预览
        preview_html = self.template.render(resume) if self.template else None
    
    # 4. Domain Model → Dict
        from dataclasses import asdict
        return {
           "resume": asdict(resume),
            "preview_html": preview_html
    }
