import os, json
from flask import render_template, current_app, jsonify

from app.models import Region
from app.blueprints.main import bp


# ------------------------------ FRONT PAGES ------------------------------


@bp.route('/')
@bp.route('/index')
def index():
    # state_props = [feature["properties"] for feature in geometry["features"]]
    # ranking = sorted(state_props, key=lambda props: props["Confirmed"]/props["Intensive-care beds"])
    # worst = ranking[-1]
    # safest = ranking[0]
    return render_template('main/home.html', title='Home', mapboxAccessToken=current_app.config['MAPBOX_ACCESS_TOKEN'])


def get_time_series_item(time_series, mdy):
    if mdy is not None and mdy in time_series:
        return [mdy, time_series[mdy]]
    else:
        return time_series.items()[-1]


@bp.route('/fetch', defaults={'mdy': None})
@bp.route('/fetch/<mdy>')
def fetch_days(mdy):

    geojson = {"type": "FeatureCollection", "features": []}
    worst = None
    safest = None
    for region in Region.query.all():
        feature = region.to_geo_feature(mdy)
        geojson["features"].append(feature)

        name = feature['properties']['name']
        cases_per_bed = feature['properties']['cases per bed']
        if worst is None or cases_per_bed > worst[1]:
            worst = [name, cases_per_bed]
        if safest is None or cases_per_bed < safest[1]:
            safest = [name, cases_per_bed]

    return jsonify({'worst': worst, 'safest': safest, 'geojson': geojson})


