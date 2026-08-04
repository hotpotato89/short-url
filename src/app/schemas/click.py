from datetime import datetime

from pydantic import BaseModel


class ClickResponse(BaseModel):
    id: int
    url_id: int
    user_ip: str
    user_agent: str

    model_config = {"from_attributes": True}
