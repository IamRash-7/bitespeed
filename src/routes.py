from flask import request, Blueprint, jsonify
from src import db
from src.models import Contact
from sqlalchemy import or_,and_

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/', methods=['GET'])
def home():
    return jsonify({"Message":"Welcome to App"})
    
@api_blueprint.route('/identify', methods=['POST'])
def identify_users():
    data = request.json
    email = data.get("email")
    phoneNumber = data.get("phoneNumber")

    # Get Primary Contact corresponding to request
    primary_contact = None
    primary_contact = Contact.query.filter(
        and_(
            or_(
                Contact.email == email, Contact.phoneNumber == phoneNumber
            ),
        Contact.linkPrecedence=="primary")
        ).order_by(Contact.createdAt).first()
    
    # Get secondary contact corresponding to request (strictly) -> Handle Null Inputs
    if email and phoneNumber is None:
        matching_contact = Contact.query.filter_by(email = email, linkPrecedence='secondary').first()
    elif phoneNumber and email is None:
        matching_contact = Contact.query.filter_by(phoneNumber = phoneNumber, linkPrecedence='secondary').first()
    else:
        matching_contact = Contact.query.filter_by(email = email, phoneNumber = phoneNumber, linkPrecedence='secondary').first()

    # Get all contacts corresponding to request (loosely) and remove our primary card from it
    existing_contacts = Contact.query.filter(or_(Contact.email == email, Contact.phoneNumber == phoneNumber)).all()
    for item in existing_contacts:
        if primary_contact and item.id == primary_contact.id:
            primary_contact = item
            existing_contacts.remove(item)

    # If primary card is present
    if primary_contact:
        # If primary card is the requested one
        if (email == primary_contact.email or email == None) and (phoneNumber == primary_contact.phoneNumber or phoneNumber == None):
            consolidated_contact = format_result(primary_contact)
            return jsonify(consolidated_contact)
        else:
            # IF Strict match is present
            if matching_contact:
                consolidated_contact = format_result(primary_contact)
                return jsonify(consolidated_contact)
            else:
                # Update loosely matching card
                if existing_contacts:
                    for existing_contact in existing_contacts:
                        existing_contact.linkPrecedence = "secondary"
                        existing_contact.linkedId = primary_contact.id
                    db.session.commit()
                    consolidated_contact = format_result(primary_contact)
                    return jsonify(consolidated_contact)
                # Create new secondary card
                else:
                    new_secondary_contact = Contact(
                        phoneNumber=phoneNumber,
                        email=email,
                        linkedId=primary_contact.id,
                        linkPrecedence="secondary"
                    )
                    db.session.add(new_secondary_contact)
                    db.session.commit()

                    consolidated_contact = format_result(primary_contact)
                    return jsonify(consolidated_contact)
    # primary card is NOT present
    else:
        # IF Strict match is present
        if matching_contact:
            primary_contact = Contact.query.get(matching_contact.linkedId)
            consolidated_contact = format_result(primary_contact)
            return jsonify(consolidated_contact)
        # Create New Primary Card
        else:
            new_primary_contact = Contact(
                    phoneNumber=phoneNumber,
                    email=email,
                    linkedId=None,
                    linkPrecedence="primary"
                )
            db.session.add(new_primary_contact)
            db.session.commit()

            return jsonify({
                "contact": {
                    "primaryContactId": new_primary_contact.id,"emails": [new_primary_contact.email],"phoneNumbers": [new_primary_contact.phoneNumber],"secondaryContactIds": []
                    }
                })


def format_result(primary_contact):
    emails = [primary_contact.email]
    phoneNumbers = [primary_contact.phoneNumber]

    # Get all linked cards (secondary)
    secondary_contact_ids = []
    secondary_contacts = Contact.query.filter_by(linkedId = primary_contact.id)
    if secondary_contacts:
        for secondary_contact in secondary_contacts:
            secondary_contact_ids.append(secondary_contact.id)

            if secondary_contact.email not in emails:
                emails.append(secondary_contact.email)

            if secondary_contact.phoneNumber not in phoneNumbers:
                phoneNumbers.append(secondary_contact.phoneNumber)

    return {
        "contact": {
            "primaryContactId": primary_contact.id,
            "emails": emails,
            "phoneNumbers": phoneNumbers,
            "secondaryContactIds": secondary_contact_ids,
        }
    }