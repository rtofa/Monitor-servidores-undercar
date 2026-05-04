from pydantic import BaseModel
from datetime import datetime

class ServerStateResponse(BaseModel):
    id: int
    server_name: str
    status: str
    last_checked: datetime
    status_changed_at: datetime

    class Config:
        from_attributes = True