from datetime import datetime

from pydantic import BaseModel


class StatsResponse(BaseModel):
    id: int
    url_id: int
    user_ip: str
    user_agent: str
    created_at: datetime

    model_config = {"from_attributes": True}
