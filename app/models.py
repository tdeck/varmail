from flask.ext.sqlalchemy import SQLAlchemy, event
import uuid
import base64
import datetime

def token():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).replace('=', '')

def short_token():
    return token().replace('-','').replace('_', '')[:12]

db = SQLAlchemy()

class TimestampMixin(object):
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def create_time(mapper, connection, instance):
        now = datetime.datetime.utcnow()
        instance.created_at = now
        instance.updated_at = now

    @staticmethod
    def update_time(mapper, connection, instance):
        now = datetime.datetime.utcnow()
        instance.updated_at = now

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'before_insert', cls.create_time)
        event.listen(cls, 'before_update', cls.update_time)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    login_token = db.Column(db.String(22), unique=True)

    endpoints = db.relationship('Endpoint', backref=db.backref('user'))

    def __init__(self, email):
        self.email = email.lower()
        self.login_token = token()

class Endpoint(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(22), unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    disabled = db.Column(db.Boolean, nullable=False, default=False)

    messages = db.relationship('Message', backref=db.backref('endpoint'))

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.token = short_token()

class Message(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)

    endpoint_id = db.Column(db.Integer, db.ForeignKey('endpoint.id'), index=True, nullable=False)
    subject = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent = db.Column(db.Boolean, nullable=False, default=False)
    reference_id = db.Column(db.String(255), nullable=True)

    reqid = db.Column(db.String(32), nullable=True, default=None)

    idx_endpoint_and_reqid = db.Index(endpoint_id, reqid, unique=True)
