# schemas.py

from pydantic import BaseModel


class CallRequest(BaseModel):
    caller_id: str
    receiver_id: str
