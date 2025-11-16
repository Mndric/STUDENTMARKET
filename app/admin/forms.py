from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length

class UserCreateForm(FlaskForm):
    username = StringField('Korisničko ime', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Uloga', choices=[('user', 'User'), ('admin', 'Admin')])
    password = PasswordField('Lozinka', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Kreiraj korisnika')

class UserEditForm(FlaskForm):
    username = StringField('Korisničko ime', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Uloga', choices=[('user', 'User'), ('admin', 'Admin')])
    submit = SubmitField('Spremi promjene')
