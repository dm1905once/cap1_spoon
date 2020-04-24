"""Populate ingredients list table with CSV files."""

from csv import DictReader
from app import db
from models import IngredientList


db.drop_all()
db.create_all()

with open('catalogues/ingredients_list.csv') as ingredients:
    db.session.bulk_insert_mappings(IngredientList, DictReader(ingredients))

db.session.commit()
