from pydantic import BaseModel
from datetime import datetime

class UPSStatus(BaseModel):
    status: str
    battery: int | None = None
    load: int | None = None
    last_update: datetime