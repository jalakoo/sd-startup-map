from pydantic import BaseModel
from typing import Optional


class Company(BaseModel):
    Name: str
    UUID: str
    Url: Optional[str] = None
    Description: Optional[str] = None
    # CreatedAt: Optional[datetime] = None
    StartupYear: Optional[int] = None
    LinkedInUrl: Optional[str] = None
    # UpdatedAt: Optional[datetime] = None
    Logo: Optional[str] = None
    Lat: Optional[float] = None
    Lon: Optional[float] = None
    Tags: Optional[list[str]] = None

    Address: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    ZipCode: Optional[str] = None


class Tag(BaseModel):
    Name: Optional[str] = ""
