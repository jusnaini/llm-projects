from pydantic import BaseModel
from typing import Optional, Dict, Any

class FormData(BaseModel):
    Upload_ID: Optional[str] = None
    version: Optional[str] = None
    saved_at: Optional[str] = None
    file_name: Optional[str] = None
    
    class Config:
        extra = "allow"  # Allow additional fields

class EvaluationRequest(BaseModel):
    extracted: Dict[str, Any]
    edited: Dict[str, Any]