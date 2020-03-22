import os

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_moment import Moment

import config


# Create application
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(config)
app.config.from_pyfile('config.py')

# Initialize Sentry if possible
if app.config['SENTRY_DSN']:
    sentry_sdk.init(
        dsn=app.config['SENTRY_DSN'],
        integrations=[FlaskIntegration(), SqlalchemyIntegration()]
    )

# Bind Flask extensions to application object
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

# Blueprints
from app import blueprints
blueprints.init_app(app)

with app.app_context():
    from app.util import filters


