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

hrr_data = index_by_key(load_data("static/hrr-data.json"), "HRR")
hrr_geojson = load_data("static/hrr.geo.json")
city_to_county = load_data("static/city-county.json")


def yield_timeseries(stats):
    for k, v in stats.items():
        dt = get_date(k)
        if dt:
            yield int(v), dt


for feature in hrr_geojson["features"]:
    hrrcity = feature["properties"]["HRRCITY"]

    region = Region.get_or_create(hrrcity)
    region.id = feature["properties"]["HRRNUM"]
    region.geometry = json.dumps(feature["geometry"])

    if hrrcity in hrr_data:
        region.total_beds = hrr_data[hrrcity]["Total Hospital Beds"]
        region.total_icu_beds = hrr_data[hrrcity]["Total ICU Beds"]
        region.available_beds = hrr_data[hrrcity]["Available Hospital Beds"]
        region.potentially_available_beds = hrr_data[hrrcity]["Potentially Available Hospital Beds*"]
        region.available_icu_beds = hrr_data[hrrcity]["Available ICU Beds"]
        region.potentially_available_icu_beds = hrr_data[hrrcity]["Potentially Available ICU Beds*"]
        region.adult_population = hrr_data[hrrcity]["Adult Population"]
        region.population_65plus = hrr_data[hrrcity]["Population 65+"]
    db.session.merge(region)

    confirmed_ts = confirmed.get(hrrcity)
    deaths_ts = confirmed.get(hrrcity)
    recovered_ts = confirmed.get(hrrcity)
    if hrrcity in city_to_county:
        county_name, state_id = city_to_county[hrrcity]
        county = county_name+", "+state_id
        county_alt = county_name+" County, "+state_id

        confirmed_ts = confirmed_ts or confirmed.get(county) or confirmed.get(county_alt)
        deaths_ts = deaths_ts or deaths.get(county) or deaths.get(county_alt)
        recovered_ts = recovered_ts or recovered.get(county) or recovered.get(county_alt)

    if confirmed_ts:
        for value, recorded_at in yield_timeseries(confirmed_ts):
            s = CoronaStat.get_or_create(Confirmed, region_id=region.id, value=value, recorded_at=recorded_at)
            db.session.merge(s)
    if deaths_ts:
        for value, recorded_at in yield_timeseries(deaths_ts):
            s = CoronaStat.get_or_create(Deaths, region_id=region.id, value=value, recorded_at=recorded_at)
            db.session.merge(s)
    if recovered_ts:
        for value, recorded_at in yield_timeseries(recovered_ts):
            s = CoronaStat.get_or_create(Recovered, region_id=region.id, value=value, recorded_at=recorded_at)
            db.session.merge(s)
db.session.commit()
