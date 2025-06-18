from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True, index=True)
    linked_id = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    link_precedence = Column(String, default="primary")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)