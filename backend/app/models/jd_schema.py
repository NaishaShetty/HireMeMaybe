from pydantic import BaseModel


class JobDescription(BaseModel):

    job_title: str | None = None

    required_skills: list[str] = []

    preferred_skills: list[str] = []

    experience_required: str | None = None

    responsibilities: list[str] = []