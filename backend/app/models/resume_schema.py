from pydantic import BaseModel


class Education(BaseModel):
    school: str


class Experience(BaseModel):
    company: str
    role: str


class Project(BaseModel):
    title: str


class Resume(BaseModel):

    email: str | None = None
    phone: str | None = None

    skills: list[str] = []

    education: list[Education] = []

    experience: list[Experience] = []

    projects: list[Project] = []