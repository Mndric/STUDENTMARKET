from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Korisničko ime', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Lozinka', validators=[DataRequired()])
    remember = BooleanField('Zapamti me')
    submit = SubmitField('Prijavi se')

class RegisterForm(FlaskForm):
    username = StringField('Korisničko ime', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Lozinka', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Potvrdi lozinku', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registriraj se')

    def validate_username(self, username):
        if User.get_by_username(username.data):
            raise ValidationError('Korisničko ime već postoji.')

    def validate_email(self, email):
        if User.get_by_email(email.data):
            raise ValidationError('Email adresa već je registrirana.')
