from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from app.models import Contact
from app.database import get_db

def get_contacts_by_email_or_phone(db: Session, email: str = None, phone_number: str = None):
    filters = []
    if email:
        filters.append(Contact.email == email)
    if phone_number:
        filters.append(Contact.phone_number == phone_number)
    
    if not filters:
        return []
    
    return db.query(Contact).filter(or_(*filters)).all()

def create_contact(db: Session, email: str = None, phone_number: str = None, linked_id: int = None):
    link_precedence = "secondary" if linked_id else "primary"
    contact = Contact(
        email=email,
        phone_number=phone_number,
        linked_id=linked_id,
        link_precedence=link_precedence
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

def get_linked_contacts(db: Session, primary_id: int):
    return db.query(Contact).filter(
        or_(
            Contact.id == primary_id,
            Contact.linked_id == primary_id
        )
    ).all()

def update_contact_to_secondary(db: Session, contact: Contact, primary_id: int):
    contact.link_precedence = "secondary"
    contact.linked_id = primary_id
    contact.updated_at = datetime.utcnow()
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact