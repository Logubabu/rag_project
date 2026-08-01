from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str

class Source(BaseModel):
    filename: str
    score: float

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]

class DocumentResponse(BaseModel):
    id: str
    filename: str
    size: int
    upload_date: str
