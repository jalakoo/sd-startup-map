from pydantic import BaseModel
from typing import Any, List, Optional

class Startup(BaseModel):
    name: str
    description: Optional[str] = ""
    url: Optional[str] = None
    address: Optional[str] = None
    latitude: float
    longitude: float