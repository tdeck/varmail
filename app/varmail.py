from models import db
from ui import ui
from api import api

from flask import Flask
from flask_limiter import Limiter
import os
import premailer
import logging
import yoyo

app_dir = os.path.dirname(__file__)
db_url = os.environ.get('DATABASE_URL')

# Run any pending migrations
backend = yoyo.get_backend(db_url)
migrations = yoyo.read_migrations(app_dir + '/../migrations')

with backend.lock():
    backend.apply_migrations(backend.to_apply(migrations))

app = Flask(__name__)

app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME')
app.config['MAILGUN_DOMAIN'] = os.environ.get('MAILGUN_DOMAIN') or os.environ.get('SERVER_NAME')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url

db.app = app
db.init_app(app)

# CSS directives must be inlined in HTML emails.
@app.template_filter('inline_styles')
def inline_styles(html):
    return premailer.transform(html)

limiter = Limiter(app, global_limits=['5/second'])
limiter.limit('100/hour')(ui)
limiter.limit('10/minute')(api)
limiter.limit('100/day')(api)

app.register_blueprint(ui)
app.register_blueprint(api)

if __name__ == '__main__':
    print "Running in debug mode"
    app.debug = True
    app.run()
else:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)
