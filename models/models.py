from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

# Pydantic model for data coming from the client or internal processing
class OCRResultBase(BaseModel):
    filename: str
    extracted_text: str

class OCRResultInDB(OCRResultBase):
    id: Optional[int] = Field(None, primary_key=True) 
    created_at: datetime = Field(default_factory=datetime.utcnow)
