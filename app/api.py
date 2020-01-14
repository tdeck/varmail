from models import Endpoint, Message, db
from mailer import send_mail

from flask import request, current_app, jsonify, abort, Blueprint
from flask_cors import cross_origin
from sqlalchemy.exc import IntegrityError

api = Blueprint('api', __name__)

@api.route('/<token>', methods=['POST'])
def post_mail(token):
    endpoint = Endpoint.query.filter_by(token=token).first_or_404()
    if endpoint.disabled:
        return abort(410)

    subject = None
    text = None
    reqid = None
    invalid_args = []
    missing_args = []

    content_type = request.headers.get('content-type')
    if content_type == 'application/json':
        subject = request.json.get('subject')
        text = request.json.get('text')
        reqid = request.json.get('_reqid')
        invalid_args = (
            (set(request.json.keys()) - {'subject', 'text', '_reqid'}).union(
                request.args.keys()
            )
        )
    elif content_type == 'application/x-www-form-urlencoded':
        subject = request.form.get('subject')
        text = request.form.get('text')
        reqid = request.form.get('_reqid')
        invalid_args = (
            (set(request.form.keys()) - {'subject', 'text', '_reqid'}).union(
                request.args.keys()
            )
        )
    else: # Assume we want to send the mail as-is
        subject = request.args.get('subject')
        reqid = request.args.get('reqid')
        text = request.data

        invalid_args = set(request.args.keys()) - {'subject', '_reqid'}

    if not subject: missing_args.append('subject')
    if not text: missing_args.append('text')

    errors = ['Invalid argument `{}`'.format(arg) for arg in invalid_args]
    errors += ['Missing required argument `{}`'.format(arg) for arg in missing_args]

    if errors:
        return "\n".join(errors), 400

    # Need to catch duplicate errors
    message = Message(endpoint_id=endpoint.id, subject=subject, body=text, reqid=reqid)
    try:
        db.session.add(message)
        db.session.commit()

        message.reference_id = send_mail(
            sender_domain = current_app.config['MAILGUN_DOMAIN'],
            sender_name = '{} - Varmail'.format(endpoint.name),
            sender_account = 'mailer',
            recipient = endpoint.user.email,
            subject = subject,
            text = text
        )

        message.sent = True
        db.session.add(message)
        db.session.commit()
    except IntegrityError as e:
        # This appears to be the only way to distinguish different types
        # of integrity errors :(
        if e.orig.pgcode != '23505': # UNIQUE VIOLATION
            raise e
        # Else swallow the error

    return 'Sent'
