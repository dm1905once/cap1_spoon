"""Forms for Spoons app."""

from flask_wtf import FlaskForm
# from models import nada
from wtforms import StringField, TextAreaField, SelectField, SelectMultipleField

class SearchByMealTypeForm(FlaskForm):
    """Form to search for recipes based on meal type options."""

    meal_type = SelectField('Search by Type of Meal')

class SearchByIngredientsForm(FlaskForm):
    """Form to search for recipes based on ingredients."""

    ingredients = SelectMultipleField('Search by Main Ingredients')
