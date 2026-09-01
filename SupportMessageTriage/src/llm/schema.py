from enum import Enum
from pydantic import BaseModel, Field

class CategoryEnum(str, Enum):
    billing = "billing"
    bug = "bug"
    feature = "feature"
    other = "other"

class UrgencyEnum(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"

class TriageInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)

class TriageOutput(BaseModel):
    category: CategoryEnum
    urgency: UrgencyEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., max_length=150)
