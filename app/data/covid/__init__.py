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


def read_csv(fp):
    with open(fp) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        headers = None
        rows = []
        for row in reader:
            if headers is None:
                headers = row
            else:
                rows.append(row)

    return headers, rows


def only_us(data):
    headers, rows = data
    header_idx = headers.index("Country/Region")
    rows = [row for row in rows if row[header_idx] == "US"]
    return headers, rows


def save(data, fn):
    with open(os.path.join(covid_dir, fn), "w") as f:
        json.dump(data, f)


confirmed_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
deaths_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
recovered_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"


print("Downloading Confirmed...")
confirmed_path = download_file(confirmed_url, "time_series_19-covid-Confirmed.csv")
print("Downloading Deaths...")
deaths_path = download_file(deaths_url, "time_series_19-covid-Deaths.csv")
print("Downloading Recovered...")
recovered_path = download_file(recovered_url, "time_series_19-covid-Recovered.csv")

# Convert confirmed to json
confirmed = only_us(read_csv(confirmed_path))
save(confirmed, "confirmed.json")

# Convert deaths to json
deaths = only_us(read_csv(deaths_path))
save(deaths, "deaths.json")

# Convert recovered to json
recovered = only_us(read_csv(recovered_path))
save(recovered, "recovered.json")

