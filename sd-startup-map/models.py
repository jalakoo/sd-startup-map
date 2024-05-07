from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional


# Or Planet
class Company(BaseModel):
    Id: int
    Description: Optional[str] = None
    # CreatedAt: Optional[datetime] = None
    StartupYear: Optional[int] = None
    LinkedInUrl: Optional[str] = None
    # UpdatedAt: Optional[datetime] = None
    Url: Optional[str] = None
    Name: Optional[str] = None
    Logo: Optional[str] = None
    Lat: Optional[float] = None
    Lon: Optional[float] = None


class Tag(BaseModel):
    Name: Optional[str] = ""
