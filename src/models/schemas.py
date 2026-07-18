from pydantic import BaseModel
from typing import Optional

# Using hardcoded default for now or we can import from core config later
DEFAULT_TZ_HOURS = 5.5

class BirthData(BaseModel):
    year: int
    month: int
    day: int
    time: str      # "HH:MM"
    lat: float = 11.0  # Default: Tamil Nadu (Coimbatore)
    lon: float = 77.0
    tz_hours: float = DEFAULT_TZ_HOURS  # hours east of UTC (IST = 5.5)
    focus: str = "general"
    lang: str = "en"
    api_key: Optional[str] = None
