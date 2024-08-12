from pydantic import BaseModel
from typing import Optional
import uuid


class Company(BaseModel):
    Name: str
    UUID: str = str(uuid.uuid4())
    Url: Optional[str] = ""
    Description: Optional[str] = ""
    # CreatedAt: Optional[datetime] = None
    StartupYear: Optional[int] = 0
    LinkedInUrl: Optional[str] = ""
    # UpdatedAt: Optional[datetime] = None
    Logo: Optional[str] = ""
    Lat: Optional[float] = 0.0
    Lon: Optional[float] = 0.0
    Tags: Optional[list[str]] = []

    Address: Optional[str] = ""
    City: Optional[str] = ""
    State: Optional[str] = ""
    ZipCode: Optional[str] = ""


class Tag(BaseModel):
    Name: Optional[str] = ""
