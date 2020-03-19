import json
import os

from config import basedir, data_dir


def load_data(fn):
    path = os.path.join(data_dir, fn)
    with open(path, "r") as f:
        data = json.load(f)
    return data


def save(data, fn):
    with open(os.path.join(data_dir, fn), "w") as f:
        json.dump(data, f)


aggregate = load_data("aggregate.json")
geometry = load_data("static/default-geometry.json")

for feature in geometry["features"]:
    name = feature["properties"]["name"]
    feature["properties"].update(aggregate[name])

save(geometry, "geometry.json")
