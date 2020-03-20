import json
import os, datetime, re

from app import db
from app.models import Region, CoronaStat, Confirmed, Deaths, Recovered
from config import basedir, data_dir


def load_data(fn):
    path = os.path.join(data_dir, fn)
    with open(path, "r") as f:
        data = json.load(f)
    return data


def to_objects(table):
    """ convert table rows to list of objects """
    headers, rows = table
    return [{headers[i]: col for i, col in enumerate(row)} for row in rows]


# def index_by_header(table, header):
#     """ index table rows by their value of a header """
#     headers, rows = table
#     header_idx = headers.index(header)
#     return {row[header_idx]: [col for i, col in enumerate(row) if i != header_idx] for row in rows}


def index_by_key(objects, key):
    """ index objects by their value of a key """
    return {obj[key]: {k: obj[k] for k in obj if k != key} for obj in objects}


def get_date(string):
    try:
        return datetime.datetime.strptime(string, '%m/%d/%y').date()
    except ValueError:
        return None


confirmed = index_by_key(to_objects(load_data("covid/confirmed.json")), "Province/State")
deaths = index_by_key(to_objects(load_data("covid/deaths.json")), "Province/State")
recovered = index_by_key(to_objects(load_data("covid/recovered.json")), "Province/State")

hospital_stats = index_by_key(to_objects(load_data("static/hospital-stats.json")), "State")

geo_features = load_data("static/default-geometry.json")["features"]


def yield_timeseries(stats):
    for k, v in stats.items():
        dt = get_date(k)
        if dt:
            yield int(v), dt


for feature in geo_features:
    state_id = int(feature["id"])
    geometry = feature["geometry"]
    name = feature["properties"]["name"]

    region = Region.get_or_create(name=name)
    region.id = state_id
    region.geometry = json.dumps(geometry)

    if name in hospital_stats:
        region.hospitals = hospital_stats[name]["Hospitals reporting"]
        region.intensive_care_beds = hospital_stats[name]["Intensive-care beds"]
        region.specialty_icu_beds = hospital_stats[name]["Specialty ICU beds"]
        region.acute_care_beds = hospital_stats[name]["Acute-care beds"]
        region.total_beds = hospital_stats[name]["Total beds"]

    if name in confirmed:
        for value, recorded_at in yield_timeseries(confirmed[name]):
            s = CoronaStat.get_or_create(Confirmed, region_id=region.id, value=value, recorded_at=recorded_at)
            db.session.merge(s)
    if name in deaths:
        for value, recorded_at in yield_timeseries(deaths[name]):
            s = CoronaStat.get_or_create(Deaths, region_id=region.id, value=value, recorded_at=recorded_at)
            db.session.merge(s)
    if name in recovered:
        for value, recorded_at in yield_timeseries(recovered[name]):
            s = CoronaStat.get_or_create(Recovered, region_id=region.id, value=value, recorded_at=recorded_at)
            db.session.merge(s)

    db.session.merge(region)
db.session.commit()
