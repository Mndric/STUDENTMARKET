from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import Optional, Length

class ProfileForm(FlaskForm):
    first_name = StringField('Ime', validators=[Optional(), Length(max=50)])
    last_name = StringField('Prezime', validators=[Optional(), Length(max=50)])
    phone = StringField('Broj mobitela', validators=[Optional(), Length(max=20)])
    profile_image = FileField('Profilna slika', validators=[FileAllowed(['jpg','jpeg','png'], 'Samo slike!')])
    submit = SubmitField('Spremi')
