"""Populate tables that show recipe search parameter at the home page."""

from csv import DictReader
from app import db
from models import IngredientList, MealTypes


db.drop_all()
db.create_all()

# Seed IngredientList from csv
with open('catalogues/ingredients_list.csv') as ingredients:
    db.session.bulk_insert_mappings(IngredientList, DictReader(ingredients))

# Seed MealTypes
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
for name,label in SPOON_MEAL_TYPES:
    new_type = MealTypes(meal_type_name=name, meal_type_label=label)
    db.session.add(new_type)

db.session.commit()
