"""Forms for Spoons app."""

from flask_wtf import FlaskForm
# from models import nada
from wtforms import StringField, PasswordField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length


### User forms
class UserRegisterForm(FlaskForm):
    """Form for registering new users."""
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name')

class UserLoginForm(FlaskForm):
    """Form to authenticate existing users."""
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    

### Recipe search forms
class SearchByMealTypeForm(FlaskForm):
    """Form to search for recipes based on meal type options."""
    meal_type = SelectField('Search by Type of Meal')

class SearchByIngredientsForm(FlaskForm):
    """Form to search for recipes based on ingredients."""
    ingredients = SelectMultipleField('Search by Main Ingredients')
