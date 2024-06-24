from datetime import datetime

from pydantic import BaseModel


class CandidateModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    created_at: datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
