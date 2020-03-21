import datetime
import json
from flask import render_template, current_app, jsonify
from sqlalchemy import cast, Float, desc, func, distinct

from app import db
from app.models import Region, Confirmed, Deaths, Recovered
from app.blueprints.main import bp


# ------------------------------ FRONT PAGE ------------------------------

@bp.route('/', defaults={'date': None})
@bp.route('/index', defaults={'date': None})
@bp.route('/<date>')
def index(date):
    recorded_dates = db.session.query(distinct(Confirmed.recorded_at)).order_by(Confirmed.recorded_at.desc())\
        .limit(18).all()
    recorded_dates = [date_fmt_string(d[0]) for d in recorded_dates]

    # if date is unspecified or is not a valid date, use latest date
    if date is None or date not in recorded_dates:
        date = recorded_dates[0]

    return render_template('main/home.html', title='Home', selected_date=date, dates=recorded_dates,
                           mapbox_access_token=current_app.config['MAPBOX_ACCESS_TOKEN'])


# ------------------------------ FETCH ------------------------------

def str_parse_date(string):
    try:
        return datetime.datetime.strptime(string, '%m-%d-%y').date()
    except ValueError:
        return None


def date_fmt_string(dt):
    return dt.strftime('%m-%d-%y')


def get_time_series_item(time_series, mdy):
    if mdy is not None and mdy in time_series:
        return [mdy, time_series[mdy]]
    else:
        return time_series.items()[-1]


@bp.route('/fetch/<date>')
def fetch(date):
    date = str_parse_date(date)
    if date is None:
        return 'Invalid date (must follow "MM-DD-YY")'

    # Just take a moment to appreciate this massive SQLAlchemy query
    results = Region.query\
        .join(Confirmed).filter(Confirmed.recorded_at == date) \
        .join(Deaths).filter(Deaths.recorded_at == date) \
        .join(Recovered).filter(Recovered.recorded_at == date) \
        .group_by(Region) \
        .add_column(Confirmed.value) \
        .add_column(Deaths.value) \
        .add_column(Recovered.value) \
        .add_column((cast(Confirmed.value, Float) / cast(Region.intensive_care_beds, Float)).label("cases_per_bed")) \
        .order_by("cases_per_bed").all()

    geojson = {"type": "FeatureCollection", "features": []}
    for (region, confirmed, deaths, recovered, cases_per_bed) in results:
        properties = {
            "name": region.name,

            "Hospitals reporting": region.hospitals,
            "Intensive-care beds": region.intensive_care_beds,
            "Specialty ICU beds": region.specialty_icu_beds,
            "Acute-care beds": region.acute_care_beds,
            "Total beds": region.total_beds,

            "confirmed": confirmed,
            "deaths": deaths,
            "recovered": recovered,

            "cases per bed": cases_per_bed
        }
        feature = {
            "type": "Feature",
            "id": str(region.id),
            "properties": properties,
            "geometry": json.loads(region.geometry)
        }
        geojson["features"].append(feature)

    return jsonify(geojson)


