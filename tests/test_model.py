from unittest import TestCase
from app import app
from datetime import datetime
from models import db, User, Recipe, Cooklist, CooklistRecipe, Ingredient, UserRecipe, UserPreference

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///spoon_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

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