from datetime import datetime
from pydantic import BaseModel


class ExportLogResponse(BaseModel):
    id: int
    user_id: int
    format: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }