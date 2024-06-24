from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class AuthorizedUser(User):
    access_token: Optional[str] = None


class CandidateModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    created_at: datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
