import datetime
from flask import render_template, current_app, jsonify

from app.models import Region
from app.blueprints.main import bp


# ------------------------------ FRONT PAGE ------------------------------

@bp.route('/', defaults={'mdy': None})
@bp.route('/index', defaults={'mdy': None})
@bp.route('/<mdy>')
def index(mdy):
    return render_template('main/home.html', title='Home', mapboxAccessToken=current_app.config['MAPBOX_ACCESS_TOKEN'],
                           mdy=mdy)


# ------------------------------ FETCH ------------------------------

def get_date(string):
    try:
        return datetime.datetime.strptime(string, '%m-%d-%y').date()
    except ValueError:
        return None


def get_time_series_item(time_series, mdy):
    if mdy is not None and mdy in time_series:
        return [mdy, time_series[mdy]]
    else:
        return time_series.items()[-1]


@bp.route('/fetch', defaults={'mdy': None})
@bp.route('/fetch/<mdy>')
def fetch_days(mdy):
    date = None if mdy is None else get_date(mdy)

    geojson = {"type": "FeatureCollection", "features": []}
    worst = None
    safest = None
    for region in Region.query.all():
        feature = region.to_geo_feature(date)
        geojson["features"].append(feature)

        name = feature['properties']['name']
        cases_per_bed = feature['properties']['cases per bed']
        if worst is None or cases_per_bed > worst[1]:
            worst = [name, cases_per_bed]
        if safest is None or cases_per_bed < safest[1]:
            safest = [name, cases_per_bed]

    return jsonify({'worst': worst, 'safest': safest, 'geojson': geojson})


