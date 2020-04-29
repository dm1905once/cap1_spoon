"""Spoon application."""

from flask import Flask, render_template, request, redirect, session, flash, g
from models import db, connect_db, User, Recipe, Cooklist, CooklistRecipe, Ingredient, UserRecipe, UserPreference, IngredientList 
from forms import SearchByMealTypeForm, SearchByIngredientsForm, UserRegisterForm, UserLoginForm
from private import SPOON_API_KEY
from recipe import Recipe
import requests
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
# from flask_debugtoolbar import DebugToolbarExtension
# debug = DebugToolbarExtension(app)

app.config['SECRET_KEY'] = "asdfasdflkgflkgf"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spoon'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
connect_db(app)

SPOON_API_URL = "https://api.spoonacular.com"
SPOON_MEAL_TYPES=[
    ("main course", "Main course"),
    ("side dish", "Side dish"),
    ("dessert", "Dessert"),
    ("appetizer","Appetizer"),
    ("salad", "Salad"),
    ("bread", "Bread"),
    ("breakfast", "Breakfast"),
    ("soup", "Soup"),
    ("beverage", "Beverage"),
    ("sauce", "Sauce"),
    ("marinade", "Marinade"),
    ("fingerfood", "Fingerfood"),
    ("snack", "Snack"),
    ("drink", "Drink")
]

### User / Session functions

CURR_USER_KEY = "current_user"

@app.before_request
def add_user_to_g():
    """If logged in, add current user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]





#### Routes ####

@app.route('/', methods=["GET"])
def home():
    meal_type_form = SearchByMealTypeForm()
    meal_type_form.meal_type.choices =  [(type[0], type[1]) for type in SPOON_MEAL_TYPES]

    ingredients_form = SearchByIngredientsForm()
    ingredients_list = IngredientList.query.all()
    ingredients_form.ingredients.choices = [(ingredient.name, ingredient.name) for ingredient in ingredients_list]

    return render_template('home.html', meal_type_form=meal_type_form, ingredients_form=ingredients_form)
    # return render_template('temp.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    """Register a new user"""

    form = UserRegisterForm()

    if form.validate_on_submit():
        try:
            new_user = User.register(
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            db.session.add(new_user)
            db.session.commit()

        except IntegrityError:
            flash("Email is already registered", 'danger')
            return render_template('users/register.html', form=form)

        do_login(new_user)

        return redirect("/")

    else:
        return render_template('users/register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = UserLoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.email.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.first_name}!", "success")
            return redirect("/")
        else:
            flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)



@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("User logged out", "info")
    return redirect('/')




@app.route('/recipes', methods=["GET"])
def list_recipes():
    """Parse search options and retrieve recipes according to search parameters."""

    args = request.args

    # Call findByIngredients  API to search by list of ingredients
    if "ingredients" in args:
        selected_ingredients='+'.join(args.getlist("ingredients"))
        resp = requests.get(f"{SPOON_API_URL}/recipes/findByIngredients", params={"apiKey":{SPOON_API_KEY}, "ingredients":selected_ingredients, "ignorePantry":"true", "ranking":1, "number":12})

        recipes = resp.json()

        if resp.status_code == 200:
            return render_template('recipes/recipes.html', recipes=recipes)
        else:
            return redirect('/')

    # Call complexSearch API to search by mealtype
    if "meal_type" in args:
        meal_type=args.get("meal_type")

        resp = requests.get(f"{SPOON_API_URL}/recipes/complexSearch", params={"apiKey":{SPOON_API_KEY}, "type":meal_type,"number":12})

        recipes = resp.json()

        if resp.status_code == 200:
            return render_template('recipes/recipes.html', recipes=recipes['results'])
        else:
            return redirect('/')




@app.route('/recipes/<int:recipe_id>', methods=["GET"])
def display_recipe_details(recipe_id):
    """Display full details of the recipe."""

    resp = requests.get(f"{SPOON_API_URL}/recipes/{recipe_id}/information", params={"apiKey":{SPOON_API_KEY}, "includeNutrition":"false"})

    recipe = resp.json()

    if resp.status_code == 200:
        return render_template('recipes/recipe_details.html', recipe=recipe)
    else:
        return redirect('/')
