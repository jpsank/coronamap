import os, json
from flask import render_template

from config import data_dir
from app.blueprints.main import bp


# ------------------------------ FRONT PAGES ------------------------------

with open(os.path.join(data_dir, "aggregate.json"), "r") as f:
    aggregate = json.load(f)

with open(os.path.join(data_dir, "geometry.json"), "r") as f:
    geometry = f.read()


@bp.route('/')
@bp.route('/index')
def index():
    worst_state = max(aggregate, key=lambda k: aggregate[k]["Confirmed"] if "Confirmed" in aggregate[k] else -1)
    return render_template('main/home.html', title='Home', statesData=geometry,
                           worst=[worst_state, aggregate[worst_state]])

