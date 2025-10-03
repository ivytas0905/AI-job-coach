from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

class PersonalInfo(BaseModel):
    name: Optional[str] = Field(..., description="The name of the candidate")
    email: Optional[str] = Field(..., description="The email of the candidate")
    phone: Optional[str] = Field(..., description="The phone number of the candidate")
    linkedin: Optional[HttpUrl] = Field(..., description="The linkedin profile of the candidate")
    github: Optional[HttpUrl] = Field(..., description="The github profile of the candidate")