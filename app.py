"""Spoon application."""

from flask import Flask, render_template, request, redirect, session, flash, g, jsonify
from models import db, connect_db, User, Recipe, Cooklist, CooklistRecipe, Ingredient, UserRecipe, UserPreference, IngredientList, MealTypes
from forms import SearchByMealTypeForm, SearchByIngredientsForm, UserRegisterForm, UserLoginForm, CooklistForm
from private import SPOON_API_KEY
import requests, json
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from datetime import datetime
from flask_paginate import Pagination

app = Flask(__name__)
app.config['SECRET_KEY'] = "asdfasdflkgflkgf"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spoon'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
connect_db(app)
SPOON_API_URL = "https://api.spoonacular.com"
CURR_USER_KEY = "current_user"
PAGINATION_PER_PAGE=12
PAGINATION_SEARCH=False

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
    
    meal_types = MealTypes.query.all()
    meal_type_form = SearchByMealTypeForm()
    meal_type_form.meal_type.choices =  [(type.meal_type_name, type.meal_type_label) for type in meal_types]

    ingredients_form = SearchByIngredientsForm()
    ingredients_list = IngredientList.query.all()
    ingredients_form.ingredients.choices = [(ingredient.name, ingredient.name) for ingredient in ingredients_list]

    return render_template('home.html', meal_type_form=meal_type_form, ingredients_form=ingredients_form)


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
        user = User.authenticate(form.email.data, form.password.data)

        if user:
            do_login(user)
            
            redirecting_user = request.form.get('redirect_after_login', None)
            if redirecting_user:
                return redirect(redirecting_user)
            else:
                return redirect("/user/favorites")
        else:
            flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    return redirect('/')


@app.route('/recipes', methods=["GET"])
def list_recipes():
    """Parse search options and retrieve recipes according to search parameters."""

    form = UserRegisterForm()
    args = request.args

    # Pagination 
    page = request.args.get('page', type=int, default=1)
    pagination_offset = (page - 1) * PAGINATION_PER_PAGE

    # Call findByIngredients  API to search by list of ingredients
    if "ingredients" in args:
        selected_ingredients='+'.join(args.getlist("ingredients"))
        resp = requests.get(f"{SPOON_API_URL}/recipes/findByIngredients", params={"apiKey":{SPOON_API_KEY}, "ingredients":selected_ingredients, "ignorePantry":"true", "ranking":1})
        recipes_list = resp.json()

    # Call complexSearch API to search by mealtype
    if "meal_type" in args:
        meal_type=args.get("meal_type")
        resp = requests.get(f"{SPOON_API_URL}/recipes/complexSearch", params={"apiKey":{SPOON_API_KEY}, "type":meal_type, "number":120})
        recipes_json = resp.json()
        recipes_list = recipes_json['results']

    if recipes_list:
        recipes = recipes_list[pagination_offset : pagination_offset+PAGINATION_PER_PAGE]
        pagination = Pagination(page=page, per_page=PAGINATION_PER_PAGE, total=len(recipes_list), search=PAGINATION_SEARCH, record_name='recipes', display_msg='Displaying recipes <b>{start} - {end}</b> of a total of {total}', css_framework='bootstrap4', alignment='center')  
        return render_template('recipes/recipes.html', recipes=recipes, form=form, pagination=pagination)
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
        new_recipe = Recipe.save(
            id      =recipe['id'],
            title   =recipe['title'],
            summary =recipe['summary'],
            image   =recipe['image'],
            ready_in_minutes=recipe['readyInMinutes'],
            servings=recipe['servings'],
            instructions=recipe['analyzedInstructions'],
            ingredients=recipe['extendedIngredients']
        )
        g.user.favorites.append(new_recipe)
        db.session.add(new_recipe)
        
    else:
        already_favorite = any(every_recipe.id == current_recipe.id for every_recipe in g.user.favorites)
        if already_favorite is False:
            new_favorite = UserRecipe(user_id=g.user.id, recipe_id=current_recipe.id)
            db.session.add(new_favorite)
    db.session.commit()

    return redirect(f'/user/favorites')


@app.route('/user/favorites', methods=["GET"])
def show_favs():

    if not g.user:
        flash("Please log in to access this content", "danger")
        return redirect("/login")

    favorites = g.user.favorites
    userlists = g.user.cooklists

    return render_template('recipes/recipes_favorites.html', favorites=favorites, userlists=userlists)


@app.route('/user/favorites', methods=["POST"])
def add_recipe_to_cooklist():

    if not g.user:
        flash("Please log in to access this content", "danger")
        return redirect("/login")

    cooklist_id = request.form.get("add-cooklist-id")
    recipe_id = request.form.get("add-recipe-id")

    new_cooklist_recipe = CooklistRecipe(recipe_id=recipe_id, cooklist_id=cooklist_id)

    if new_cooklist_recipe:
        db.session.add(new_cooklist_recipe)
        db.session.commit()
        flash(f"Recipe added succesfully", "success")
    else:
        flash(f"Error adding recipe to cooklist", "error")

    favorites = g.user.favorites
    userlists = g.user.cooklists
        
    return render_template('recipes/recipes_favorites.html', favorites=favorites, userlists=userlists)

@app.route('/user/favorites/remove_recipe', methods=["POST"])
def remove_favorite_recipe():

    if not g.user:
        flash("Please log in to access this content", "danger")
        return redirect("/login")

    recipe_id = request.form.get("delete-recipe-id")

    remove_recipe_favorite = UserRecipe.query.filter(UserRecipe.user_id==g.user.id, UserRecipe.recipe_id==recipe_id).first()

    if remove_recipe_favorite:
        # Remove recipe from favorites list
        db.session.delete(remove_recipe_favorite)
        # Remove recipe from user cooklists
        remove_recipe_cooklists = CooklistRecipe.query.filter(CooklistRecipe.recipe_id==recipe_id,CooklistRecipe.cooklist_id.in_(list.id for list in g.user.cooklists)).all()
        for entry in remove_recipe_cooklists:
            db.session.delete(entry)

        db.session.commit()
        flash(f"Recipe removed succesfully", "success")
    else:
        flash(f"Error removing recipe from Favorites", "error")

    favorites = g.user.favorites
    userlists = g.user.cooklists
        
    return render_template('recipes/recipes_favorites.html', favorites=favorites, userlists=userlists)


@app.route('/cooklists/new', methods=["GET", "POST"])
def create_cooklist():

    if not g.user:
        flash("Please log in to access this content", "danger")
        return redirect("/login")

    form = CooklistForm()

    if form.validate_on_submit():
        list_name   = request.form.get('list_name')
        description = request.form.get('description', None)
        new_cooklist = Cooklist(user_id=g.user.id, list_name=list_name, description=description, created_date=datetime.now())
        db.session.add(new_cooklist)
        db.session.commit()

        flash(f"Cooklist {list_name} added successfully", "success")
        return redirect("/user/cooklists")

    else:
        return render_template('cooklists/new_cooklist.html', form=form)


@app.route('/user/cooklists', methods=["GET"])
def show_cooklists():
    """Display user cooklists or handle parameters to create a new one"""

    if not g.user:
        flash("Please log in to access this content", "danger")
        return redirect("/login")

    cooklists = Cooklist.query.filter(Cooklist.user_id == g.user.id).order_by(desc('created_date')).all()

    return render_template('cooklists/cooklists.html', cooklists=cooklists)


@app.route('/user/cooklists/remove_recipe', methods=["POST"])
def remove_recipe_from_cooklist():
    """Remove a recipe from a cooklist"""

    if not g.user:
        flash("Please log in to access this content", "danger")
        return redirect("/login")

    cooklist_id = request.form.get("data-cooklist-id")
    recipe_id = request.form.get("data-recipe-id")

    remove_cooklist_recipe = CooklistRecipe.query.filter(CooklistRecipe.recipe_id==recipe_id, CooklistRecipe.cooklist_id==cooklist_id).first()

    if remove_cooklist_recipe:
        db.session.delete(remove_cooklist_recipe)
        db.session.commit()
        flash(f"Recipe removed succesfully", "success")
    else:
        flash(f"Error removing recipe from cooklist", "error")

    cooklists = Cooklist.query.filter(Cooklist.user_id == g.user.id).order_by(desc('created_date')).all()

    return render_template('cooklists/cooklists.html', cooklists=cooklists)