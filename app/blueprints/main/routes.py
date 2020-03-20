import os, json
from flask import render_template, current_app

from config import data_dir
from app.blueprints.main import bp


# ------------------------------ FRONT PAGES ------------------------------

with open(os.path.join(data_dir, "geometry.json"), "r") as f:
    geometry = json.load(f)


@bp.route('/')
@bp.route('/index')
def index():
    state_props = [feature["properties"] for feature in geometry["features"]]
    ranking = sorted(state_props, key=lambda props: props["Confirmed"]/props["Intensive-care beds"])
    worst = ranking[-1]
    safest = ranking[0]
    return render_template('main/home.html', title='Home', mapboxAccessToken=current_app.config['MAPBOX_ACCESS_TOKEN'],
                           statesData=json.dumps(geometry),
                           worst=worst, safest=safest)

