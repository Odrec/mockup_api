from pydantic import BaseModel
from typing import List, Optional, Dict


class QuotaDefinition(BaseModel):
    type: Optional[str]
    description: Dict[str, str]
    reset_interval: Optional[str]
    scope: str
    feature: Optional[str] = None


class QuotaGet(BaseModel):
    limit: int
    used: Optional[int] = None
    type: Optional[str]
    scope: str
    feature: Optional[str] = None
    user_id: Optional[str] = None


class QuotaUpdate(BaseModel):
    limit: int
    scope: str
    feature: Optional[str] = None
    user_id: Optional[str] = None  # Dennis: It is not specified. Do we need this in put routes?


class Metadata(BaseModel):
    tool_url: str
    quota_url: str
    image_url: str
    description: Dict[str, str]
    title: Dict[str, str]
    supported_quotas: List[QuotaDefinition]

    # Dennis: What is the purpose of this class?
    class Config:
        arbitrary_types_allowed = True
