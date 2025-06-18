from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class ContactBase(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None

class IdentifyRequest(BaseModel):
    email: Optional[str] = None
    phoneNumber: Optional[str] = None

class ContactResponse(BaseModel):
    primaryContactId: int
    emails: List[str]
    phoneNumbers: List[str]
    secondaryContactIds: List[int]

class IdentifyResponse(BaseModel):
    contact: ContactResponse

class ContactOut(BaseModel):
    id: int
    phone_number: Optional[str]
    email: Optional[str]
    linked_id: Optional[int]
    link_precedence: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True