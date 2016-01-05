from models import db
from ui import ui
from api import api

from flask import Flask
import os
import premailer
import logging

app = Flask(__name__)

app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db.app = app
db.init_app(app)

# CSS directives must be inlined in HTML emails.
@app.template_filter('inline_styles')
def inline_styles(html):
    return premailer.transform(html)

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
