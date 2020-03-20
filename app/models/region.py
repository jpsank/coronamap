from sqlalchemy import func

from app import db
from app.models.base import Base


class Region(Base):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))

    hospitals = db.Column(db.Integer)
    intensive_care_beds = db.Column(db.Integer)
    specialty_icu_beds = db.Column(db.Integer)
    acute_care_beds = db.Column(db.Integer)
    total_beds = db.Column(db.Integer)

    geometry = db.Column(db.String)

    confirmed = db.relationship('Confirmed', backref='region', lazy='dynamic')
    deaths = db.relationship('Deaths', backref='region', lazy='dynamic')
    recovered = db.relationship('Recovered', backref='region', lazy='dynamic')

    def __repr__(self):
        return '<Region {}>'.format(self.name)

    # Custom queries

    @staticmethod
    def get_or_create(name):
        existing = Region.query.filter(func.lower(Region.name) == func.lower(name)).first()
        return existing if existing is not None else Region(name=name)
