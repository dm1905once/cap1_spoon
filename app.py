"""Spoon application."""

from flask import Flask, render_template, request, redirect
from models import db, connect_db, User, Recipe, Cooklist, CooklistRecipe, Ingredient, UserRecipe, UserPreference, IngredientList 
from forms import SearchByMealTypeForm
from private import SPOON_API_KEY
from recipe import Recipe
import requests

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

@app.route('/, methods=["GET"]')
def home():
    meal_type_form = SearchByMealTypeForm()
    meal_type_form.meal_type.choices =  [(type[0], type[1]) for type in SPOON_MEAL_TYPES]
    return render_template('home.html', meal_type_form=meal_type_form)

@app.route('/recipes', methods=["GET"])
def list_recipes():
    """Parse search options and retrieve recipes according to search parameters."""

    args = request.args

    # Call __  API to search by list of ingredients
    if "ingredients" in args:
        # Call ingredients API
        print("nada")

    # Call complexSearch API to search by mealtype
    if "meal_type" in args:
        meal_type=args.get("meal_type")

        resp = requests.get(f"{SPOON_API_URL}/recipes/complexSearch", params={"apiKey":{SPOON_API_KEY}, "type":meal_type,"number":12})
        # import pdb
        # pdb.set_trace()
        # print("Cool")

        recipes = resp.json()

        if resp.status_code != 200:
            print("NOT cool")
            return redirect('/')


    return render_template('recipes.html', recipes=recipes['results'])