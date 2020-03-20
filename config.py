import os
basedir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(basedir, "app/data")


# CONFIGURATION

DEBUG = True

# Logging
LOGS_PATH = os.path.join(basedir, 'logs')

# Flask-SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
