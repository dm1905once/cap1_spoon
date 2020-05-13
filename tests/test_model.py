from unittest import TestCase
from app import app
from datetime import datetime
from models import db, User, Recipe, Cooklist, CooklistRecipe, Ingredient, UserRecipe, UserPreference

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spoon_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True

db.drop_all()
db.create_all()


class SpoonModelTestCase(TestCase):
    """Test DB model of the Spoon application"""

    def setUp(self):
        """Create test client, add sample data."""
        UserRecipe.query.delete()
        Recipe.query.delete()
        Cooklist.query.delete()
        UserPreference.query.delete()
        User.query.delete()

    def tearDown(self):
        """Clean up transactions."""
        db.session.rollback()


    def test_create_user(self):
        """Test create users"""

        new_user = User.register(email="test1@test.com",
                                    password="testuser1",
                                    first_name="User1",
                                    last_name="LastName1",
                                    measure_system="metric")

        db.session.add(new_user)
        
        all_users = User.query.all()
        self.assertEqual(len(all_users), 1)
        self.assertNotEqual(new_user.password, "testuser1")

    
    def test_authenticate_user(self):
        """Test user authentication"""

        new_user = User.register(email="test1@test.com",
                                    password="testuser1",
                                    first_name="User1",
                                    last_name="LastName1",
                                    measure_system="metric")

        db.session.add(new_user)

        auth_user = User.authenticate("test1@test.com", "testuser1")
        self.assertIsInstance(auth_user, User)

        invalid_pwd = User.authenticate("test1@test.com", "abc123")
        self.assertEqual(invalid_pwd, False)


    def test_create_cooklist(self):
        """Test create a new cooklist"""

        new_user = User.register(email="test1@test.com",
                                    password="testuser1",
                                    first_name="User1",
                                    last_name="LastName1",
                                    measure_system="metric")

        db.session.add(new_user)

        new_cooklist = Cooklist(user_id=new_user.id,
            list_name="Test cooklist1",
            description="Test cooklist model",
            created_date=datetime.now())

        self.assertIsInstance(new_cooklist, Cooklist)


    def test_create_recipe(self):
        """Test create recipe"""

        new_recipe = Recipe.save(
            id      = 523145,
            title   = "Nutella Overnight Dessert Oats",
            summary = "Summary goes in here",
            image   = "https://spoonacular.com/recipeImages/523145-556x370.jpg",
            ready_in_minutes = 45,
            servings = 1,
            instructions = [{"name": "", "steps": [{"equipment": [{"id": 404783, "image": "bowl.jpg", "name": "bowl"}], "ingredients": [], "number": 1, "step": "In a medium-sized serving bowl, add the Step 1 ingredients and stir"}, {"equipment": [{"id": 404730, "image": "plastic-wrap.jpg", "name": "plastic wrap"}], "ingredients": [], "number": 2, "step": "Add the Step 2 ingredients and stir again.  Cover with plastic wrap and let sit in the fridge overnight.  Enjoy first thing in the morning!"}]}],
            ingredients = [{"aisle": "Milk, Eggs, Other Dairy", "amount": 0.3333333333333333, "consistency": "liquid", "id": 93607, "image": "almond-milk.png", "measures": {"metric": {"amount": 78.863, "unitLong": "milliliters", "unitShort": "ml"}, "us": {"amount": 0.333, "unitLong": "cups", "unitShort": "cups"}}, "meta": ["unsweetened"], "metaInformation": ["unsweetened"], "name": "almond milk", "original": "1/3-1/2 cup Unsweetened Almond Milk", "originalName": "Unsweetened Almond Milk", "originalString": "1/3-1/2 cup Unsweetened Almond Milk", "unit": "cup"}, {"aisle": "Milk, Eggs, Other Dairy", "amount": 1.0, "consistency": "solid", "id": 1001, "image": "butter-sliced.jpg", "measures": {"metric": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}, "us": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}}, "meta": [], "metaInformation": [], "name": "butter", "original": "1 Tbs Natural Hazelnut Butter", "originalName": "Natural Hazelnut Butter", "originalString": "1 Tbs Natural Hazelnut Butter", "unit": "Tbs"}, {"aisle": "Health Foods", "amount": 32.0, "consistency": "solid", "id": 99075, "image": "chocolate-protein-powder.jpg", "measures": {"metric": {"amount": 32.0, "unitLong": "grams", "unitShort": "g"}, "us": {"amount": 1.129, "unitLong": "ounces", "unitShort": "oz"}}, "meta": [], "metaInformation": [], "name": "chocolate protein powder", "original": "1 32g scoop Chocolate Protein Powder", "originalName": "Chocolate Protein Powder", "originalString": "1 32g scoop Chocolate Protein Powder", "unit": "g"}, {"aisle": "Baking", "amount": 1.0, "consistency": "solid", "id": 19165, "image": "cocoa-powder.png", "measures": {"metric": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}, "us": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}}, "meta": ["unsweetened", "()"], "metaInformation": ["unsweetened", "()"], "name": "cocoa powder", "original": "1 Tbs Regular Cocoa Powder (unsweetened)", "originalName": "Regular Cocoa Powder (unsweetened)", "originalString": "1 Tbs Regular Cocoa Powder (unsweetened)", "unit": "Tbs"}, {"aisle": "Health Foods;Baking", "amount": 1.0, "consistency": "solid", "id": 12220, "image": "flax-seeds.png", "measures": {"metric": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}, "us": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}}, "meta": [], "metaInformation": [], "name": "ground flaxseed", "original": "1 Tbs Ground Flaxseed", "originalName": "Ground Flaxseed", "originalString": "1 Tbs Ground Flaxseed", "unit": "Tbs"}, {"aisle": "Cereal", "amount": 0.5, "consistency": "solid", "id": 8120, "image": "rolled-oats.jpg", "measures": {"metric": {"amount": 118.294, "unitLong": "milliliters", "unitShort": "ml"}, "us": {"amount": 0.5, "unitLong": "cups", "unitShort": "cups"}}, "meta": [], "metaInformation": [], "name": "old fashioned rolled oats", "original": "1/2 cup Old Fashioned Rolled Oats", "originalName": "Old Fashioned Rolled Oats", "originalString": "1/2 cup Old Fashioned Rolled Oats", "unit": "cup"}, {"aisle": "Spices and Seasonings", "amount": 0.0625, "consistency": "solid", "id": 2047, "image": "salt.jpg", "measures": {"metric": {"amount": 0.063, "unitLong": "teaspoons", "unitShort": "tsps"}, "us": {"amount": 0.063, "unitLong": "teaspoons", "unitShort": "tsps"}}, "meta": [], "metaInformation": [], "name": "salt", "original": "1/16 tsp Salt", "originalName": "Salt", "originalString": "1/16 tsp Salt", "unit": "tsp"}, {"aisle": "Baking", "amount": 2.0, "consistency": "solid", "id": 99190, "image": "sugar-substitute.jpg", "measures": {"metric": {"amount": 2.0, "unitLong": "packets", "unitShort": "packets"}, "us": {"amount": 2.0, "unitLong": "packets", "unitShort": "packets"}}, "meta": [], "metaInformation": [], "name": "sukrin sweetener", "original": "2-5 packets Sweetener*", "originalName": "Sweetener", "originalString": "2-5 packets Sweetener*", "unit": "packets"}]
        )

        self.assertIsInstance(new_recipe, Recipe)
        all_ingredients = Ingredient.query.all()

        self.assertEqual(len(all_ingredients), 8)


    def test_recipe_operations(self):
        """Test recipe operations: create, add as favorite, add to cooklist"""

        # Create user
        new_user = User.register(email="test1@test.com",
                                    password="testuser1",
                                    first_name="User1",
                                    last_name="LastName1",
                                    measure_system="metric")
        db.session.add(new_user)


        # Create new cooklist
        new_cooklist = Cooklist(user_id=new_user.id,
            list_name="Test cooklist1",
            description="Test cooklist model",
            created_date=datetime.now())
        db.session.add(new_cooklist)

        # Create recipe
        new_recipe = Recipe.save(
            id      = 523145,
            title   = "Nutella Overnight Dessert Oats",
            summary = "Summary goes in here",
            image   = "https://spoonacular.com/recipeImages/523145-556x370.jpg",
            ready_in_minutes = 45,
            servings = 1,
            instructions = [{"name": "", "steps": [{"equipment": [{"id": 404783, "image": "bowl.jpg", "name": "bowl"}], "ingredients": [], "number": 1, "step": "In a medium-sized serving bowl, add the Step 1 ingredients and stir"}, {"equipment": [{"id": 404730, "image": "plastic-wrap.jpg", "name": "plastic wrap"}], "ingredients": [], "number": 2, "step": "Add the Step 2 ingredients and stir again.  Cover with plastic wrap and let sit in the fridge overnight.  Enjoy first thing in the morning!"}]}],
            ingredients = [{"aisle": "Milk, Eggs, Other Dairy", "amount": 0.3333333333333333, "consistency": "liquid", "id": 93607, "image": "almond-milk.png", "measures": {"metric": {"amount": 78.863, "unitLong": "milliliters", "unitShort": "ml"}, "us": {"amount": 0.333, "unitLong": "cups", "unitShort": "cups"}}, "meta": ["unsweetened"], "metaInformation": ["unsweetened"], "name": "almond milk", "original": "1/3-1/2 cup Unsweetened Almond Milk", "originalName": "Unsweetened Almond Milk", "originalString": "1/3-1/2 cup Unsweetened Almond Milk", "unit": "cup"}, {"aisle": "Milk, Eggs, Other Dairy", "amount": 1.0, "consistency": "solid", "id": 1001, "image": "butter-sliced.jpg", "measures": {"metric": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}, "us": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}}, "meta": [], "metaInformation": [], "name": "butter", "original": "1 Tbs Natural Hazelnut Butter", "originalName": "Natural Hazelnut Butter", "originalString": "1 Tbs Natural Hazelnut Butter", "unit": "Tbs"}, {"aisle": "Health Foods", "amount": 32.0, "consistency": "solid", "id": 99075, "image": "chocolate-protein-powder.jpg", "measures": {"metric": {"amount": 32.0, "unitLong": "grams", "unitShort": "g"}, "us": {"amount": 1.129, "unitLong": "ounces", "unitShort": "oz"}}, "meta": [], "metaInformation": [], "name": "chocolate protein powder", "original": "1 32g scoop Chocolate Protein Powder", "originalName": "Chocolate Protein Powder", "originalString": "1 32g scoop Chocolate Protein Powder", "unit": "g"}, {"aisle": "Baking", "amount": 1.0, "consistency": "solid", "id": 19165, "image": "cocoa-powder.png", "measures": {"metric": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}, "us": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}}, "meta": ["unsweetened", "()"], "metaInformation": ["unsweetened", "()"], "name": "cocoa powder", "original": "1 Tbs Regular Cocoa Powder (unsweetened)", "originalName": "Regular Cocoa Powder (unsweetened)", "originalString": "1 Tbs Regular Cocoa Powder (unsweetened)", "unit": "Tbs"}, {"aisle": "Health Foods;Baking", "amount": 1.0, "consistency": "solid", "id": 12220, "image": "flax-seeds.png", "measures": {"metric": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}, "us": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}}, "meta": [], "metaInformation": [], "name": "ground flaxseed", "original": "1 Tbs Ground Flaxseed", "originalName": "Ground Flaxseed", "originalString": "1 Tbs Ground Flaxseed", "unit": "Tbs"}, {"aisle": "Cereal", "amount": 0.5, "consistency": "solid", "id": 8120, "image": "rolled-oats.jpg", "measures": {"metric": {"amount": 118.294, "unitLong": "milliliters", "unitShort": "ml"}, "us": {"amount": 0.5, "unitLong": "cups", "unitShort": "cups"}}, "meta": [], "metaInformation": [], "name": "old fashioned rolled oats", "original": "1/2 cup Old Fashioned Rolled Oats", "originalName": "Old Fashioned Rolled Oats", "originalString": "1/2 cup Old Fashioned Rolled Oats", "unit": "cup"}, {"aisle": "Spices and Seasonings", "amount": 0.0625, "consistency": "solid", "id": 2047, "image": "salt.jpg", "measures": {"metric": {"amount": 0.063, "unitLong": "teaspoons", "unitShort": "tsps"}, "us": {"amount": 0.063, "unitLong": "teaspoons", "unitShort": "tsps"}}, "meta": [], "metaInformation": [], "name": "salt", "original": "1/16 tsp Salt", "originalName": "Salt", "originalString": "1/16 tsp Salt", "unit": "tsp"}, {"aisle": "Baking", "amount": 2.0, "consistency": "solid", "id": 99190, "image": "sugar-substitute.jpg", "measures": {"metric": {"amount": 2.0, "unitLong": "packets", "unitShort": "packets"}, "us": {"amount": 2.0, "unitLong": "packets", "unitShort": "packets"}}, "meta": [], "metaInformation": [], "name": "sukrin sweetener", "original": "2-5 packets Sweetener*", "originalName": "Sweetener", "originalString": "2-5 packets Sweetener*", "unit": "packets"}]
        )
        db.session.add(new_recipe)

        # Add recipe to favorites
        new_favorite = UserRecipe(user_id=new_user.id, recipe_id=new_recipe.id)
        db.session.add(new_favorite)

        all_favorites = UserRecipe.query.all()
        self.assertEqual(len(all_favorites), 1)

        # Add favorite recipe to cooklist
        new_cooklist_recipe = CooklistRecipe(recipe_id=new_recipe.id, cooklist_id=new_cooklist.id)
        db.session.add(new_cooklist_recipe)

        all_cooklist_recipes = CooklistRecipe.query.all()
        self.assertEqual(len(all_cooklist_recipes), 1)


        



        