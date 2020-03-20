from sqlalchemy import func

from app import db
from app.models.base import Base


class CoronaStat(Base):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    recorded_at = db.Column(db.Date)

    @staticmethod
    def get_or_create(cls, region_id, value, recorded_at):
        existing = cls.query.filter_by(region_id=region_id, recorded_at=recorded_at).first()
        if existing is not None:
            existing.value = value
            return existing
        else:
            return cls(region_id=region_id, value=value, recorded_at=recorded_at)

    def serialize(self):
        return [self.value, self.recorded_at.strftime('%m/%d/%y')]


class Confirmed(CoronaStat):
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))


class Deaths(CoronaStat):
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))


class Recovered(CoronaStat):
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))

