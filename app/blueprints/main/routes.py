import datetime
import json
from flask import render_template, current_app, jsonify
from sqlalchemy import cast, Float, desc, func, distinct

from app import db
from app.models import Region, CoronaStat
from app.blueprints.main import bp


# ------------------------------ FRONT PAGE ------------------------------

@bp.route('/', defaults={'date': None})
@bp.route('/index', defaults={'date': None})
@bp.route('/<date>')
def index(date):
    dates = db.session.query(distinct(CoronaStat.date)).order_by(CoronaStat.date.desc()).limit(18).all()
    dates = [dump_date(d[0]) for d in dates]

    # if date is unspecified or is not a valid date, use latest date
    if date is None or date not in dates:
        date = dates[0]

    return render_template('main/home.html', title='Home', selected_date=date, dates=dates,
                           mapbox_access_token=current_app.config['MAPBOX_ACCESS_TOKEN'])


# ------------------------------ FETCH ------------------------------

def load_date(string):
    try:
        return datetime.datetime.strptime(string, '%m-%d-%y').date()
    except ValueError:
        return None


def dump_date(dt):
    return dt.strftime('%m-%d-%y')


def dump_datetime(value):
    """Deserialize datetime object into iso format for JSON processing."""
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')


def get_time_series_item(time_series, mdy):
    if mdy is not None and mdy in time_series:
        return [mdy, time_series[mdy]]
    else:
        return time_series.items()[-1]


@bp.route('/fetch/<date>')
def fetch(date):
    date = load_date(date)
    if date is None:
        return 'Invalid date (must follow "MM-DD-YY")'

    # Just take a moment to appreciate this SQL query
    # Note: for some reason computing the max date also selects for it?
    results = Region.query\
        .join(CoronaStat).filter(CoronaStat.date <= date) \
        .group_by(Region) \
        .add_column(func.max(CoronaStat.date)) \
        .add_column(CoronaStat.checked_at) \
        .add_column(CoronaStat.positive) \
        .add_column(CoronaStat.negative) \
        .add_column(CoronaStat.pending) \
        .add_column(CoronaStat.hospitalized) \
        .add_column(CoronaStat.death) \
        .add_column(CoronaStat.total_tests) \
        .add_column((cast(CoronaStat.positive, Float) / cast(Region.total_icu_beds, Float)).label("cases_per_bed")) \
        .order_by(desc("cases_per_bed")).all()

    geojson = {"type": "FeatureCollection", "features": []}
    for (region, date, checked_at, positive, negative, pending, hospitalized, death, total_tests,
         cases_per_bed) in results:
        properties = {
            "full_name": region.full_name,
            "name": region.name,

            "Total Hospital Beds": region.total_beds,
            "Total ICU Beds": region.total_icu_beds,
            "Available Hospital Beds": region.available_beds,
            "Potentially Available Hospital Beds*": region.potentially_available_beds,
            "Available ICU Beds": region.available_icu_beds,
            "Potentially Available ICU Beds*": region.potentially_available_icu_beds,
            "Adult Population": region.adult_population,
            "Population 65+": region.population_65plus,

            "date": dump_date(date),
            "checked_at": dump_datetime(checked_at),

            "positive": positive,
            "negative": negative,
            "pending": pending,
            "hospitalized": hospitalized,
            "death": death,
            "total_tests": total_tests,

            "cases_per_bed": cases_per_bed
        }
        feature = {
            "type": "Feature",
            "id": str(region.id),
            "properties": properties,
            "geometry": json.loads(region.geometry)
        }
        geojson["features"].append(feature)

    return jsonify(geojson)


