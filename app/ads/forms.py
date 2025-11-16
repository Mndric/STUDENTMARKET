from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

CATEGORIES = [
    ('knjige', 'Knjige'),
    ('skripte', 'Skripte'),
    ('namjestaj', 'Namještaj'),
    ('tehnika', 'Tehnika'),
    ('oprema', 'Studentska oprema'),
    ('odjeca', 'Odjeća / obuća'),
    ('ostalo', 'Ostalo')
]

AD_TYPES = [
    ('prodaja', 'Prodaja'),
    ('razmjena', 'Razmjena'),
    ('poklanjanje', 'Poklanjanje')
]

class AdForm(FlaskForm):
    title = StringField('Naslov', validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Opis', validators=[DataRequired(), Length(min=20, max=5000)])
    price = DecimalField('Cijena (HRK)', validators=[Optional(), NumberRange(min=0)])
    category = SelectField('Kategorija', choices=CATEGORIES, validators=[DataRequired()])
    ad_type = SelectField('Vrsta oglasa', choices=AD_TYPES, validators=[DataRequired()])
    location = StringField('Lokacija', validators=[Optional(), Length(max=100)])
    image = FileField('Slika', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Samo slike!')])
    submit = SubmitField('Spremi')
