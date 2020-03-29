from sqlalchemy import func

from app import db
from app.models.base import Base


class CoronaStat(Base):
    id = db.Column(db.Integer, primary_key=True)
    region_name = db.Column(db.Integer, db.ForeignKey('region.name'))

    total_tests = db.Column(db.Integer)
    positive = db.Column(db.Integer, nullable=True)
    negative = db.Column(db.Integer, nullable=True)
    pending = db.Column(db.Integer, nullable=True)
    hospitalized = db.Column(db.Integer, nullable=True)
    death = db.Column(db.Integer, nullable=True)

    date = db.Column(db.Date)
    checked_at = db.Column(db.DateTime)

    @classmethod
    def get_or_create(cls, **kwargs):
        existing = cls.query.filter_by(**kwargs).first()
        if existing is not None:
            return existing
        else:
            return cls(**kwargs)

