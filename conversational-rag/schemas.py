from pydantic import BaseModel
from datetime import datetime

class BookingRequest(BaseModel):
    name: str
    email: str
    date: datetime
    time: str

class ChatRequest(BaseModel):
    session_id: str
    query: str

class DocumentUploadRequest(BaseModel):
    filename : str 
    content : str 
    