from src import db
import datetime

class Contact(db.Model):
    __tablename__ = 'contact'

    id = db.Column(db.Integer, primary_key=True)
    phoneNumber = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False)
    linkedId = db.Column(db.Integer, db.ForeignKey('contact.id'))
    linkPrecedence = db.Column(db.String, default = "primary", nullable = False)
    createdAt = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.datetime.utcnow)