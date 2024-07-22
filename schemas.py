import enum

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ResetIntervalDefinition(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    semester = "semester"


# Enum definitions
class QuotaScope(enum.Enum):
    user = "user"
    course = "course"
    course_user = "course-user"
    total = "total"


class QuotaDefinition(BaseModel):
    type: Optional[str]
    description: Dict[str, str]
    reset_interval: Optional[ResetIntervalDefinition]
    scope: QuotaScope
    feature: Optional[str] = None


class QuotaGet(BaseModel):
    limit: int
    used: Optional[int] = None
    type: Optional[str]
    scope: QuotaScope
    feature: Optional[str] = None
    user_id: Optional[str] = None


class QuotaUpdate(BaseModel):
    limit: int
    scope: QuotaScope
    feature: Optional[str] = None


class Metadata(BaseModel):
    tool_url: str
    quota_url: str
    image_url: str
    description: Dict[str, str]
    title: Dict[str, str]
    supported_quotas: List[QuotaDefinition]


class JWTPayload(BaseModel):
    sub: str
    name: str
    iat: int
    exp: int
    context: Optional[str]
    context_role: str = Field(alias="context-role")
