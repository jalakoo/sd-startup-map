from pydantic import BaseModel
from typing import Any, List, Optional

class Startup(BaseModel):
    name: str
    description: Optional[str] = ""
    url: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    state: Optional[str] = ""
    zip: Optional[str] = ""
    latitude: float
    longitude: float