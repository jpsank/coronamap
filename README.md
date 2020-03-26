# COVID-19 cases vs. ICU capacity map

A daily-updating choropleth map that shows confirmed COVID-19 cases per ICU bed for each US state.

## Sources
Hospital stats from [Harvard Global Health Institute](https://globalepidemics.org/2020/03/17/caring-for-covid-19-patients/)

Daily COVID-19 data from [COVID Tracking Project](https://covidtracking.com/)

## Installation
Installation is pretty simple. Clone the repo, then install python dependencies with pipenv:

`pipenv install`

Next, you can run the scraper manually with the `cron.sh` script:

`./cron.sh`

which will scrape COVID-19 data, aggregate it with hospital stats and GeoJSON, and insert it into a database.
This will then be displayed as a map when the user views the website.

Once you've scraped the data, go ahead and start the flask server, which resides in the run.py file.

### Configuration
The following vars need to be put in a `config.py` file inside an `instance` dir in the root of the repo. 

- `MAPBOX_ACCESS_TOKEN`: An access token for [Mapbox](https://www.mapbox.com/). It's required for the map background.

- `SENTRY_DSN`: A DSN for Sentry. If provided, Sentry error reporting is setup.

An example would look like this
```python
# An access token for Mapbox. It's required for the map background.
MAPBOX_ACCESS_TOKEN = "wq.s12eD3dad21xd34g23bacs4s2c3x4ebg2muc42fdsfsfsf"

# A DSN for sentry. If provided, sentry error reporting is set up.
SENTRY_DSN = "123123@sentry.io/32423432"
```

### Daily Update
Add the contents of the [cron.txt](cron.txt) file to your crontab to activate daily running of the scraper.

## Website
![A view of the homepage](screenshots/homepage.png)

Once the server is up and running, this, along with some more information below, is what users see.
