from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Set
from app import models, schemas, crud
from app.database import SessionLocal, engine, get_db
from app.schemas import IdentifyRequest, IdentifyResponse, ContactOut


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/identify", response_model=IdentifyResponse)
async def identify_contact(request: IdentifyRequest, db: Session = Depends(crud.get_db)):
    email = request.email
    phone_number = request.phoneNumber
    
    if not email and not phone_number:
        raise HTTPException(status_code=400, detail="At least one of email or phoneNumber must be provided")
    
    # Find matching contacts
    matching_contacts = crud.get_contacts_by_email_or_phone(db, email, phone_number)
    
    if not matching_contacts:
        # Create new primary contact
        new_contact = crud.create_contact(db, email, phone_number)
        return format_response(new_contact, db)
    
    # Find the primary contact (oldest primary or primary of secondaries)
    primary_contact = find_primary_contact(matching_contacts, db)
    
    # Check if we need to create a new secondary contact
    existing_emails = {c.email for c in matching_contacts if c.email}
    existing_phones = {c.phone_number for c in matching_contacts if c.phone_number}
    
    new_email_provided = email and email not in existing_emails
    new_phone_provided = phone_number and phone_number not in existing_phones
    
    if new_email_provided or new_phone_provided:
        crud.create_contact(
            db, 
            email if new_email_provided else None,
            phone_number if new_phone_provided else None,
            primary_contact.id
        )
    
    # Convert any other primary contacts to secondary
    for contact in matching_contacts:
        if contact.link_precedence == "primary" and contact.id != primary_contact.id:
            crud.update_contact_to_secondary(db, contact, primary_contact.id)
    
    return format_response(primary_contact, db)

def find_primary_contact(contacts: List[models.Contact], db: Session) -> models.Contact:
    # Find all primary contacts in the matches
    primary_contacts = [c for c in contacts if c.link_precedence == "primary"]
    
    if primary_contacts:
        # Return the oldest primary contact
        return min(primary_contacts, key=lambda x: x.created_at)
    
    # If no primary contacts, find their primary contacts
    primary_ids = {c.linked_id for c in contacts if c.linked_id}
    if primary_ids:
        primary_contacts = db.query(models.Contact).filter(
            models.Contact.id.in_(primary_ids),
            models.Contact.link_precedence == "primary"
        ).all()
        if primary_contacts:
            return min(primary_contacts, key=lambda x: x.created_at)
    
    # Fallback: return the oldest contact (shouldn't normally happen)
    return min(contacts, key=lambda x: x.created_at)

def format_response(primary_contact: models.Contact, db: Session) -> IdentifyResponse:
    linked_contacts = crud.get_linked_contacts(db, primary_contact.id)
    
    emails = list({c.email for c in linked_contacts if c.email})
    phone_numbers = list({c.phone_number for c in linked_contacts if c.phone_number})
    secondary_ids = [c.id for c in linked_contacts if c.link_precedence == "secondary"]
    
    # Ensure primary contact's info comes first
    if primary_contact.email in emails:
        emails.remove(primary_contact.email)
        emails.insert(0, primary_contact.email)
    if primary_contact.phone_number in phone_numbers:
        phone_numbers.remove(primary_contact.phone_number)
        phone_numbers.insert(0, primary_contact.phone_number)
    
    return IdentifyResponse(
        contact={
            "primaryContactId": primary_contact.id,
            "emails": emails,
            "phoneNumbers": phone_numbers,
            "secondaryContactIds": secondary_ids
        }
    )


@app.get("/contacts", response_model=List[ContactOut])
def get_all_contacts(db: Session = Depends(get_db)):
    contacts = db.query(models.Contact).all()
    return contacts