from pydantic import BaseModel
from typing import List, Optional, Dict, Literal, TypeAlias

QuotaScope: TypeAlias = Literal["user", "course", "course-user", "total"]
ResetIntervalDefinition: TypeAlias = Literal["daily", "weekly", "monthly", "semester"]


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
