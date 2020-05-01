"""Spoon application."""

from flask import Flask, render_template, request, redirect, session, flash, g, jsonify
from models import db, connect_db, User, Recipe, Cooklist, CooklistRecipe, Ingredient, UserRecipe, UserPreference, IngredientList 
from forms import SearchByMealTypeForm, SearchByIngredientsForm, UserRegisterForm, UserLoginForm
from private import SPOON_API_KEY
import requests, json
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
                last_name=form.last_name.data,
                measure_system=form.measure_system.data
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


@app.route('/recipes/favorites/<int:recipe_id>', methods=["POST"])
def add_recipe_to_favs(recipe_id):

    if not g.user:
        flash("Please log in to access this section", "danger")
        return redirect("/login")
    
    recipe_body = request.form['recipe-body-json']
    recipe = json.loads(recipe_body)

    current_recipe = Recipe.query.get(str(recipe['id']))
    
    if current_recipe is None:
        analyzedInstructions=recipe['analyzedInstructions'][0]['steps'] if recipe['analyzedInstructions'] else None
        new_recipe = Recipe(
            id      =recipe['id'],
            title   =recipe['title'],
            summary =recipe['summary'],
            image   =recipe['image'],
            ready_in_minutes=recipe['readyInMinutes'],
            servings=recipe['servings'],
            instructions=analyzedInstructions
        )
        g.user.favorites.append(new_recipe)
        db.session.add(new_recipe)

        #Here's where we populate the ingredients table
        
    else:
        already_favorite = any(every_recipe.id == current_recipe.id for every_recipe in g.user.favorites)
        if already_favorite is False:
            new_favorite = UserRecipe(user_id=g.user.id, recipe_id=current_recipe.id)
            db.session.add(new_favorite)
    db.session.commit()

    return redirect(f'/user/{g.user.id}/favorites')


@app.route('/user/<int:user_id>/favorites', methods=["GET"])
def show_favs(user_id):

    if not g.user or g.user != user_id:
        flash("Please log in to access this content", "danger")
        return redirect("/login")
    
    favorites = g.user.favorites

    return render_template('recipes/recipes_favorites.html', favorites=favorites)