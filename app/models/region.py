from sqlalchemy import func

from app import db
from app.models.base import Base


class Region(Base):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    full_name = db.Column(db.String(300))

    total_beds = db.Column(db.Integer)
    total_icu_beds = db.Column(db.Integer)
    available_beds = db.Column(db.Integer)
    potentially_available_beds = db.Column(db.Integer)  # based on 50% reduction in current occupation of beds
    available_icu_beds = db.Column(db.Integer)
    potentially_available_icu_beds = db.Column(db.Integer)  # based on 50% reduction in current occupation of beds
    adult_population = db.Column(db.Integer)
    population_65plus = db.Column(db.Integer)

    geometry = db.Column(db.String)

    stats = db.relationship('CoronaStat', backref='region', lazy='dynamic')

    def __repr__(self):
        return '<Region {}>'.format(self.name)

    # Custom queries

    @staticmethod
    def get(name):
        return Region.query.filter(func.lower(Region.name) == func.lower(name)).first()

    @staticmethod
    def get_or_create(name):
        existing = Region.get(name)
        return existing if existing is not None else Region(name=name)
