from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from datetime import datetime


class ProcessRequest(BaseModel):
    email: EmailStr
    article_url: HttpUrl


class ProcessResponse(BaseModel):
    session_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    session_id: str
    status: str  # "processing" | "completed" | "error"
    summary: Optional[str] = None
    insights: Optional[List[str]] = None
    article_url: Optional[str] = None
    created_at: Optional[str] = None
    error: Optional[str] = None


class N8nCallback(BaseModel):
    session_id: str
    summary: Optional[str] = None
    insights: Optional[List[str] | str] = None  # n8n might send string or list
    status: str = "completed"
    error: Optional[str] = None
