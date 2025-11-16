from flask import current_app, url_for
from flask_mail import Message
from app import mail
from itsdangerous import URLSafeTimedSerializer

def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-verification')

def verify_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-verification', max_age=expiration)
        return email
    except:
        return None

def send_verification_email(user):
    token = generate_verification_token(user.email)
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    msg = Message('Potvrdite svoj email - Student Market', recipients=[user.email])
    msg.body = f"""Poštovani {user.username},

Hvala što ste se registrirali na Student Market!

Molimo potvrdite svoju email adresu klikom na sljedeći link:
{verify_url}

Link je valjan 1 sat.

Ako niste vi kreirali ovaj račun, molimo zanemarite ovaj email.

Srdačan pozdrav,
Student Market tim
"""
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print("Greska pri slanju emaila:", e)
        return False
