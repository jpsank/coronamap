import json
import os, datetime, re

from app import db
from app.models import Region, CoronaStat
from config import basedir, data_dir


def load_data(fn):
    path = os.path.join(data_dir, fn)
    with open(path, "r") as f:
        data = json.load(f)
    return data


def index_by_key(objects, key):
    """ index objects by their value of a key """
    return {obj[key]: {k: obj[k] for k in obj if k != key} for obj in objects}


states_daily = load_data("covid/states_daily.json")
hospital_data = index_by_key(load_data("static/hospital-data.json"), "State")
geojson = load_data("static/states.geo.json")


for feature in geojson["features"]:
    state_id = int(feature["id"])
    name = feature["properties"]["name"]
    full = feature["properties"]["full"]

    region = Region.get_or_create(name=name)
    region.id = state_id
    region.full_name = full
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
    db.session.merge(region)
db.session.commit()


for stat in states_daily:
    recorded_at = datetime.datetime.strptime(str(stat["date"]), '%Y%m%d').date()
    cs = CoronaStat.get_or_create(region_name=stat["state"], recorded_at=recorded_at)
    cs.positive = stat["positive"]
    cs.negative = stat["negative"]
    cs.pending = stat["pending"]
    cs.hospitalized = stat["hospitalized"]
    cs.death = stat["death"]
    cs.total_tests = stat["total"]
    db.session.merge(cs)
db.session.commit()
