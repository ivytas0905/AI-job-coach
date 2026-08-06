from agent_service.domain.models import JobDescription, MasterResume, Skill
from agent_service.domain.resume_policies import select_skills


def test_skill_selection_prioritizes_jd_matches_and_preserves_order():
    resume = MasterResume(skills=[Skill("Python"), Skill(None), Skill("Go"), Skill("SQL")])
    jd = JobDescription(required_skills=["sql"], preferred_skills=["python"])

    assert select_skills(resume, jd, limit=3) == ["Python", "SQL", "Go"]


def test_skill_selection_respects_limit():
    resume = MasterResume(skills=[Skill(str(index)) for index in range(20)])
    assert len(select_skills(resume, JobDescription(), limit=15)) == 15
