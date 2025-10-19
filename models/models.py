from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class OCRResultBase(BaseModel):
    filename: str
    extracted_text: str

class OCRResultInDB(OCRResultBase):
    id: Optional[int] = Field(None, primary_key=True) 
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FeedbackBase(BaseModel):
    comment: str

class FeedbackInDB(FeedbackBase):
    id: int
    created_at: datetime