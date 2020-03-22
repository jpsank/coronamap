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

hospital_data = index_by_key(load_data("static/hospital-data.json"), "State")

geojson = load_data("static/states.geo.json")


def yield_timeseries(stats):
    for k, v in stats.items():
        dt = get_date(k)
        if dt:
            yield int(v), dt


for feature in geojson["features"]:
    state_id = int(feature["id"])
    name = feature["properties"]["name"]

    region = Region.get_or_create(name=name)
    region.id = state_id
    region.geometry = json.dumps(feature["geometry"])

    if name in hospital_data:
        region.total_beds = hospital_data[name]["Total Hospital Beds"]
        region.total_icu_beds = hospital_data[name]["Total ICU Beds"]
        region.available_beds = hospital_data[name]["Available Hospital Beds"]
        region.potentially_available_beds = hospital_data[name]["Potentially Available Hospital Beds*"]
        region.available_icu_beds = hospital_data[name]["Available ICU Beds"]
        region.potentially_available_icu_beds = hospital_data[name]["Potentially Available ICU Beds*"]
        region.adult_population = hospital_data[name]["Adult Population"]
        region.population_65plus = hospital_data[name]["Population 65+"]

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
