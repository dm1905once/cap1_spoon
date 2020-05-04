"""Forms for Spoons app."""

from flask_wtf import FlaskForm
# from models import nada
from wtforms import StringField, TextAreaField, PasswordField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length

MSG_MAX_LENGTH_30 = 'Input should not exceed 30 characters'
MSG_MAX_LENGTH_50 = 'Input should not exceed 50 characters'


### User forms
class UserRegisterForm(FlaskForm):
    """Form for registering new users."""
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=50, message=MSG_MAX_LENGTH_50)])
    password = PasswordField('Password', validators=[Length(min=6)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=30, message=MSG_MAX_LENGTH_30)])
    last_name = StringField('Last Name', validators=[Length(max=30, message=MSG_MAX_LENGTH_30)])
    measure_system = SelectField('Measure System', choices=[('metric','Metric'), ('us', 'US')])

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

### Cooklist form
class CooklistForm(FlaskForm):
    """Form for adding cooklists."""

    list_name   = StringField("Cooklist Name", validators=[DataRequired(), Length(max=30, message=MSG_MAX_LENGTH_30)])
    description = TextAreaField("Description", validators=[Length(max=50, message=MSG_MAX_LENGTH_50)])
