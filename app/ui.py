from models import User, Endpoint, Message, db
from mailer import send_mail

from flask import (
    Blueprint,
    current_app,
    session,
    request,
    redirect,
    abort,
    url_for,
    jsonify,
    render_template
)
from validate_email import validate_email
from time import time

SESSION_LIFETIME_S = 259200 # 3 days
EXPECTED_PASSWORD = '5d7660d3-c18e-46f7-ad75-1103875e6d5c'

ui = Blueprint('ui', __name__)

def make_session_permanent():
    session.permanent = True
    current_app.permanent_session_lifetime = SESSION_LIFETIME_S

ui.before_request(make_session_permanent)

def current_user():
    if 'uid' not in session or session['expiry'] < time():
        return None
    return User.query.filter_by(id=session['uid']).first()

def require_user():
    if 'uid' not in session or session['expiry'] < time():
        abort(401)
    return User.query.filter_by(id=session['uid']).first_or_404()

def request_ip():
    return (
            request.environ.get('HTTP_X_FORWARDED_FOR') or
            request.environ['REMOTE_ADDR']
    )

##############
# HTML Pages #
##############
@ui.route('/', methods=['GET'])
def home():
    user = current_user()
    return render_template('web/home.html', email=user and user.email)

@ui.route('/start', methods=['POST'])
def start():
    if 'email' not in request.form:
        return abort(400)

    if request.form.get('password') != EXPECTED_PASSWORD:
        # Password is a fake field that's set to a constant value in JS. The
        # hope is that bots will either stuff it with something or leave it
        # out because they won't a full headless browser
        print "IP {} tried to submit password {}".format(
            request_ip(),
            request.form.get('password')
        )
        return abort(403) # Forbidden

    email = request.form['email']
    if not validate_email(email):
        return abort(422)

    email = email.lower()

    user = User.query.filter_by(email=email).first()
    if user:
        subject = 'Your login link'
        template = 'mail/login.html'
    else:
        user = User(email, signup_ip=request_ip())
        db.session.add(user)
        db.session.commit()
        subject = 'Get started with varmail'
        template = 'mail/start.html'

    link = url_for('ui.login', login_token=user.login_token, _external=True)

    send_mail(
        sender_domain = current_app.config['MAILGUN_DOMAIN'],
        sender_name = 'Varmail Login',
        sender_account = 'login',
        recipient = email,
        subject = subject,
        html=render_template(template, link=link)
    )

    # Count that we sent a login email
    user.login_count = User.login_count + 1 # increment in SQL
    db.session.add(user)
    db.session.commit()

    return render_template('web/start.html')

@ui.route('/login/<login_token>', methods=['GET'])
def login(login_token):
    user = User.query.filter_by(login_token=login_token).first_or_404()

    session['uid'] = user.id
    session['expiry'] = int(time()) + SESSION_LIFETIME_S

    return redirect(url_for('ui.dashboard'))

@ui.route('/dashboard')
def dashboard():
    user = require_user()
    return render_template(
        'web/dashboard.html',
        email = user.email,
        endpoints = [present_endpoint(e) for e in user.endpoints]
    )

@ui.route('/logout', methods=['GET'])
def logout():
  session.clear()
  return redirect(url_for('ui.home'))

############
# JSON API #
############
def present_endpoint(endpoint):
    return {
        'id': endpoint.id,
        'token': endpoint.token,
        'name': endpoint.name,
        'disabled': endpoint.disabled
    }

@ui.route('/ui/endpoints', methods=['GET'])
def list_endpoints():
    user = require_user()
    return jsonify([present_endpoint(e) for e in user.endpoints])

@ui.route('/ui/endpoints', methods=['POST'])
def create_ednpoint():
    user = require_user()
    if request.json.keys() != ['name']:
        return abort(400)

    name = request.json['name']
    if not name:
        return abort(400)

    endpoint = Endpoint(user.id, name)
    db.session.add(endpoint)
    db.session.commit()

    return jsonify(present_endpoint(endpoint))

@ui.route('/ui/endpoints/<eid>', methods=['PUT'])
def update_endpoint(eid):
    user = require_user()

    if request.json.keys() - {'name', 'disabled'}:
        return abort(400)

    endpoint = Endpoint.filter_by(id=eid, user_id=user.id).first_or_404()

    if 'name' in request.json:
        endpoint.name = request.json['name']
    if 'disabled' in request.json:
        endpoint.disabled = request.json['disabled']

    db.session.add(endpoint)
    db.session.commit()

    return jsonify(present_endpoint(endpoint))
