import json
import os
import csv
import requests

from config import basedir, data_dir


covid_dir = os.path.join(data_dir, "covid")


def download_file(url, fn):
    r = requests.get(url)
    path = os.path.join(covid_dir, fn)
    with open(path, 'wb') as f:
        f.write(r.content)
    return path


download_file("https://covidtracking.com/api/states/daily", "states_daily.json")
download_file("https://covidtracking.com/api/states", "states_current.json")
