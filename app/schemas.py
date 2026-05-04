from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ServerStateResponse(BaseModel):
    id: int
    server_name: str
    status: str
    last_checked: datetime
    status_changed_at: datetime
    cpu_usage: Optional[float] = None
    ram_usage: Optional[float] = None
    gpu_usage: Optional[float] = None

class ServerEventResponse(BaseModel):
    id: int
    server_name: str
    event_type: str
    message: str
    timestamp: datetime
    
    class Config:
        from_attributes = True