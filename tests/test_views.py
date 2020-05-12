from unittest import TestCase
from flask import jsonify
from app import app, CURR_USER_KEY
from models import db, User, Recipe, Cooklist, CooklistRecipe, Ingredient, UserRecipe, UserPreference

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spoon_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()


class SpoonViewsTestCase(TestCase):
    """Test views of the Spoon application"""

    def setUp(self):
        """Create test client, add sample data."""
        UserRecipe.query.delete()
        Recipe.query.delete()
        Cooklist.query.delete()
        UserPreference.query.delete()
        User.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.register(email="test1@test.com",
                                    password="testuser1",
                                    first_name="User 1",
                                    last_name="LastName 1",
                                    measure_system="metric")

        db.session.add(self.testuser1)
        db.session.commit()


    def test_display_home(self):
        with app.test_client() as client:
            resp = client.get("/")
            self.assertEqual(resp.status_code, 200)

    def test_display_login(self):
        with app.test_client() as client:
            resp = client.get("/login")
            self.assertEqual(resp.status_code, 200)

    def test_display_register(self):
        with app.test_client() as client:
            resp = client.get("/register")
            self.assertEqual(resp.status_code, 200)

    def test_display_favorites_login_error(self):
        with app.test_client() as client:
            resp = client.get("/user/favorites")
            self.assertEqual(resp.status_code, 302)

    def test_display_cooklists_login_error(self):
        with app.test_client() as client:
            resp = client.get("/user/cooklists")
            self.assertEqual(resp.status_code, 302)

    def test_display_cooklists_new_login_error(self):
        with app.test_client() as client:
            resp = client.get("/cooklists/new")
            self.assertEqual(resp.status_code, 302)


    def test_access_user_recipes(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser1.id
            resp = client.get("/user/favorites")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("Logged in as User 1", html)
            self.assertIn("Your favorite recipes", html)


    def test_access_user_cooklists(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser1.id
            resp = client.get("/user/cooklists")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("Logged in as User 1", html)
            self.assertIn("Your cooklists", html)


    def test_access_user_new_cooklist(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser1.id
            resp = client.get("/cooklists/new")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("Logged in as User 1", html)
            self.assertIn("New cooklist", html)


    def test_create_new_cooklist(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser1.id

            # Post(Create) a new cooklist
            resp_post = client.post("/cooklists/new", data={
                "list_name": "TEST cooklist",
                "description": "First TEST cooklist"
                })
            self.assertEqual(resp_post.status_code, 302)

            # Now access the cooklists and see the newly created cooklist
            resp_get = client.get("/user/cooklists")
            self.assertEqual(resp_get.status_code, 200)

            html = resp_get.get_data(as_text=True)
            self.assertIn("Logged in as User 1", html)
            self.assertIn("TEST cooklist", html)

    def test_browse_recipes(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser1.id

            resp = client.get("/recipes?meal_type=dessert")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            recipe_card_count = html.count("card-body")
            self.assertIn("Logged in as User 1", html)
            self.assertIn("Browse recipes", html)
            self.assertEqual(recipe_card_count, 12)


    def test_view_recipe_detail(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser1.id

            resp = client.get("/recipes/523145")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("Recipe details", html)
            self.assertIn("You should know", html)
            self.assertIn("Instructions", html)
            self.assertIn("Ingredients", html)
            self.assertIn("Meal Type", html)


    def test_save_recipe_as_favorite(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session[CURR_USER_KEY] = self.testuser1.id

            # Save recipe to favorites
            fav_recipe = '{"analyzedInstructions": [{"name": "", "steps": [{"equipment": [{"id": 404783, "image": "bowl.jpg", "name": "bowl"}], "ingredients": [], "number": 1, "step": "In a medium-sized serving bowl, add the Step 1 ingredients and stir"}, {"equipment": [{"id": 404730, "image": "plastic-wrap.jpg", "name": "plastic wrap"}], "ingredients": [], "number": 2, "step": "Add the Step 2 ingredients and stir again.  Cover with plastic wrap and let sit in the fridge overnight.  Enjoy first thing in the morning!"}]}], "cuisines": [], "dishTypes": ["dessert"], "extendedIngredients": [{"aisle": "Milk, Eggs, Other Dairy", "amount": 0.3333333333333333, "consistency": "liquid", "id": 93607, "image": "almond-milk.png", "measures": {"metric": {"amount": 78.863, "unitLong": "milliliters", "unitShort": "ml"}, "us": {"amount": 0.333, "unitLong": "cups", "unitShort": "cups"}}, "meta": ["unsweetened"], "metaInformation": ["unsweetened"], "name": "almond milk", "original": "1/3-1/2 cup Unsweetened Almond Milk", "originalName": "Unsweetened Almond Milk", "originalString": "1/3-1/2 cup Unsweetened Almond Milk", "unit": "cup"}, {"aisle": "Milk, Eggs, Other Dairy", "amount": 1.0, "consistency": "solid", "id": 1001, "image": "butter-sliced.jpg", "measures": {"metric": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}, "us": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}}, "meta": [], "metaInformation": [], "name": "butter", "original": "1 Tbs Natural Hazelnut Butter", "originalName": "Natural Hazelnut Butter", "originalString": "1 Tbs Natural Hazelnut Butter", "unit": "Tbs"}, {"aisle": "Health Foods", "amount": 32.0, "consistency": "solid", "id": 99075, "image": "chocolate-protein-powder.jpg", "measures": {"metric": {"amount": 32.0, "unitLong": "grams", "unitShort": "g"}, "us": {"amount": 1.129, "unitLong": "ounces", "unitShort": "oz"}}, "meta": [], "metaInformation": [], "name": "chocolate protein powder", "original": "1 32g scoop Chocolate Protein Powder", "originalName": "Chocolate Protein Powder", "originalString": "1 32g scoop Chocolate Protein Powder", "unit": "g"}, {"aisle": "Baking", "amount": 1.0, "consistency": "solid", "id": 19165, "image": "cocoa-powder.png", "measures": {"metric": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}, "us": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}}, "meta": ["unsweetened", "()"], "metaInformation": ["unsweetened", "()"], "name": "cocoa powder", "original": "1 Tbs Regular Cocoa Powder (unsweetened)", "originalName": "Regular Cocoa Powder (unsweetened)", "originalString": "1 Tbs Regular Cocoa Powder (unsweetened)", "unit": "Tbs"}, {"aisle": "Health Foods;Baking", "amount": 1.0, "consistency": "solid", "id": 12220, "image": "flax-seeds.png", "measures": {"metric": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}, "us": {"amount": 1.0, "unitLong": "Tb", "unitShort": "Tbs"}}, "meta": [], "metaInformation": [], "name": "ground flaxseed", "original": "1 Tbs Ground Flaxseed", "originalName": "Ground Flaxseed", "originalString": "1 Tbs Ground Flaxseed", "unit": "Tbs"}, {"aisle": "Cereal", "amount": 0.5, "consistency": "solid", "id": 8120, "image": "rolled-oats.jpg", "measures": {"metric": {"amount": 118.294, "unitLong": "milliliters", "unitShort": "ml"}, "us": {"amount": 0.5, "unitLong": "cups", "unitShort": "cups"}}, "meta": [], "metaInformation": [], "name": "old fashioned rolled oats", "original": "1/2 cup Old Fashioned Rolled Oats", "originalName": "Old Fashioned Rolled Oats", "originalString": "1/2 cup Old Fashioned Rolled Oats", "unit": "cup"}, {"aisle": "Spices and Seasonings", "amount": 0.0625, "consistency": "solid", "id": 2047, "image": "salt.jpg", "measures": {"metric": {"amount": 0.063, "unitLong": "teaspoons", "unitShort": "tsps"}, "us": {"amount": 0.063, "unitLong": "teaspoons", "unitShort": "tsps"}}, "meta": [], "metaInformation": [], "name": "salt", "original": "1/16 tsp Salt", "originalName": "Salt", "originalString": "1/16 tsp Salt", "unit": "tsp"}, {"aisle": "Baking", "amount": 2.0, "consistency": "solid", "id": 99190, "image": "sugar-substitute.jpg", "measures": {"metric": {"amount": 2.0, "unitLong": "packets", "unitShort": "packets"}, "us": {"amount": 2.0, "unitLong": "packets", "unitShort": "packets"}}, "meta": [], "metaInformation": [], "name": "sukrin sweetener", "original": "2-5 packets Sweetener*", "originalName": "Sweetener", "originalString": "2-5 packets Sweetener*", "unit": "packets"}], "healthScore": 58.0, "id": 523145, "image": "https://spoonacular.com/recipeImages/523145-556x370.jpg", "imageType": "jpg", "readyInMinutes": 45, "servings": 1, "sourceName": "Desserts with Benefits", "spoonacularScore": 97.0, "summary": "Summary goes here", "title": "Nutella Overnight Dessert Oats"}'
            resp_post = client.post("/recipes/favorites/523145", data={"recipe-body-json": fav_recipe})
            self.assertEqual(resp_post.status_code, 302)

            # Now go to favorites and confirm recipe is there
            resp = client.get("/user/favorites")
            self.assertEqual(resp.status_code, 200)

            html = resp.get_data(as_text=True)
            self.assertIn("Logged in as User 1", html)
            self.assertIn("Your favorite recipes", html)
            self.assertIn("Nutella Overnight Dessert Oats", html)

             # Create a cooklist
            resp_post1 = client.post("/cooklists/new", data={
                "list_name": "TEST cooklist",
                "description": "First TEST cooklist"
                })
            self.assertEqual(resp_post1.status_code, 302)

            new_cooklist_id = db.session.query(Cooklist.id).filter(Cooklist.list_name == "TEST cooklist").first()

            # Add the favorite recipe to the cooklist
            resp_post2 = client.post("/user/favorites", data={
                "add-cooklist-id": new_cooklist_id[0],
                "add-recipe-id": 523145
                })
            self.assertEqual(resp_post2.status_code, 200)

            # Now access the cooklists and see the newly created cooklist
            resp_get = client.get("/user/cooklists")
            self.assertEqual(resp_get.status_code, 200)

            html = resp_get.get_data(as_text=True)
            self.assertIn("Logged in as User 1", html)
            self.assertIn("Your cooklists", html)
            self.assertIn("Nutella Overnight Dessert Oats", html)