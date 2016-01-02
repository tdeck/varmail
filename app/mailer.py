import requests
import os

mailgun_key = os.environ.get('MAILGUN_KEY')

def send_mail(sender_domain, sender_name, sender_account, recipient, subject, text=None, html=None):
    """
    Sends an email and returns a reference ID string.
    """
    msg_data = {
        'from': '{} <{}@{}>'.format(sender_name, sender_account, sender_domain),
        'to': [recipient],
        'subject': subject
    }
    if text:
        msg_data['text'] = text
    elif html:
        msg_data['html'] = html
    else:
        raise ValueError('Expected html or text body')

    print "Sending", msg_data

    resp = requests.post(
        'https://api.mailgun.net/v3/{}/messages'.format(sender_domain),
        auth=("api", mailgun_key),
        data=msg_data
    )
    resp.raise_for_status()

    return 'mailgun: ' + resp.json()['id']
