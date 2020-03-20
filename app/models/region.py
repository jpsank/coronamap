import json
from sqlalchemy import func

from app import db
from app.models.base import Base
from app.models.coronastat import Confirmed, Deaths, Recovered


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

    # Serializing to GeoJSON

    def get_coronastat_datum(self, cls, relationship, date=None):
        if date is not None:
            exists = relationship.filter_by(recorded_at=date).first()
            if exists is not None:
                return exists
        return relationship.order_by(cls.recorded_at.desc()).first()

    def to_geo_feature(self, date=None):
        confirmed = self.get_coronastat_datum(Confirmed, self.confirmed, date)
        deaths = self.get_coronastat_datum(Deaths, self.deaths, date)
        recovered = self.get_coronastat_datum(Recovered, self.recovered, date)

        return {
            "type": "Feature",
            "id": str(self.id),
            "properties": {"name": self.name,

                           "Hospitals reporting": self.hospitals,
                           "Intensive-care beds": self.intensive_care_beds,
                           "Specialty ICU beds": self.specialty_icu_beds,
                           "Acute-care beds": self.acute_care_beds,
                           "Total beds": self.total_beds,

                           "confirmed": confirmed.serialize(),
                           "deaths": deaths.serialize(),
                           "recovered": recovered.serialize(),

                           "cases per bed": confirmed.value/self.intensive_care_beds},
            "geometry": json.loads(self.geometry)
        }
