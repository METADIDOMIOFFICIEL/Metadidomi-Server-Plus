from pydantic import BaseModel
from typing import Dict, Any, Optional

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class ProjectOut(ProjectCreate):
    id: int
    class Config:
        from_attributes = True

class ApiCreate(BaseModel):
    name: str
    path: str
    method: str = "GET"
    response_json: Dict[str, Any]
    status_code: int = 200
    enabled: bool = True
    delay_ms: int = 0
    api_key: str = ""
    base_url: str = ""
    quota: int = 0
    quota_period: str = "hour"
    project_id: Optional[int] = None

class ApiOut(ApiCreate):
    id: int
    class Config:
        from_attributes = True

class NasCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    config_json: Dict[str, Any] = {}
    enabled: bool = True

class NasOut(NasCreate):
    id: int
    class Config:
        from_attributes = True

class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[str] = None
