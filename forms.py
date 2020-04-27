"""Forms for Spoons app."""

from flask_wtf import FlaskForm
# from models import nada
from wtforms import StringField, TextAreaField, SelectField

class SearchByMealTypeForm(FlaskForm):
    """Form to select meal type options."""

    meal_type = SelectField('Search by Type of Meal')
