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


def to_key_value(data, key_header, value_idx, return_value_header=True):
    headers, rows = data
    key_idx = headers.index(key_header)
    result = {row[key_idx]: row[value_idx] for row in rows}
    if return_value_header:
        return result, headers[value_idx]
    return result


def to_dict(data, key_header):
    headers, rows = data
    key_idx = headers.index(key_header)
    return {row[key_idx]: {headers[i]: col for i, col in enumerate(row) if i != key_idx}
            for row in rows}


confirmed, confirmed_date = to_key_value(load_data("covid/confirmed.json"), "Province/State", -1)
deaths, deaths_date = to_key_value(load_data("covid/deaths.json"), "Province/State", -1)
recovered, recovered_date = to_key_value(load_data("covid/recovered.json"), "Province/State", -1)

hospital_stats = to_dict(load_data("static/hospital-stats.json"), "State")
states = load_data("static/states.json")

aggregate = {}

for name in states:
    aggregate[name] = {}
    if name in hospital_stats:
        aggregate[name].update(hospital_stats[name])
    if name in confirmed:
        aggregate[name]["Confirmed"] = int(confirmed[name])
        aggregate[name]["Confirmed Date"] = confirmed_date
    if name in deaths:
        aggregate[name]["Deaths"] = int(deaths[name])
        aggregate[name]["Deaths Date"] = deaths_date
    if name in recovered:
        aggregate[name]["Recovered"] = int(recovered[name])
        aggregate[name]["Recovered Date"] = recovered_date

save(aggregate, "aggregate.json")


