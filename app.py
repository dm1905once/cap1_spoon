"""Spoon application."""

from flask import Flask, render_template, request, redirect
from models import db, connect_db, User, Recipe, Cooklist, CooklistRecipe, Ingredient, UserRecipe, UserPreference, IngredientList 
from forms import SearchByMealTypeForm, SearchByIngredientsForm
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

@app.route('/', methods=["GET"])
def home():
    meal_type_form = SearchByMealTypeForm()
    meal_type_form.meal_type.choices =  [(type[0], type[1]) for type in SPOON_MEAL_TYPES]

    ingredients_form = SearchByIngredientsForm()
    ingredients_list = IngredientList.query.all()
    ingredients_form.ingredients.choices = [(ingredient.name, ingredient.name) for ingredient in ingredients_list]
    # import pdb
    # pdb.set_trace()

    return render_template('home.html', meal_type_form=meal_type_form, ingredients_form=ingredients_form)
    # return render_template('temp.html')

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
