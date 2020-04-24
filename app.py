"""Spoon application."""

from flask import Flask, render_template, request, redirect
from models import db, connect_db, User, Recipe, Cooklist, CooklistRecipe, Ingredient, UserRecipe, UserPreference, IngredientList 

app = Flask(__name__)
# from flask_debugtoolbar import DebugToolbarExtension
# debug = DebugToolbarExtension(app)

app.config['SECRET_KEY'] = "asdfasdflkgflkgf"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spoon'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
connect_db(app)