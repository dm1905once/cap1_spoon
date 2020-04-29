from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


######### RECIPES #########
class Recipe(db.Model):
    '''Recipes table'''
    __tablename__ = "recipes"

    id                = db.Column(db.String(50), primary_key=True)
    title             = db.Column(db.String(50), nullable=False)
    summary           = db.Column(db.String(250), nullable=True)
    image             = db.Column(db.String(50), nullable=True)
    ready_in_minutes  = db.Column(db.Integer, nullable=True)
    servings          = db.Column(db.Integer, nullable=True)
    instructions      = db.Column(db.JSON, nullable=False)


######### COOKLISTS #########
class Cooklist(db.Model):
    '''Cooklist table. Like Playlists, but for cooking'''
    __tablename__ = "cooklists"

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    list_name    = db.Column(db.String(50), nullable=False)
    description  = db.Column(db.String(250), nullable=True)
    created_date = db.Column(db.DateTime, nullable=False)


######### COOKLISTS < RECIPES #########
class CooklistRecipe(db.Model):
    '''Recipes associated with a cooklist'''
    __tablename__ = "cooklists_recipes"

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id    = db.Column(db.String(50), db.ForeignKey('recipes.id', ondelete='CASCADE'))
    cooklist_id  = db.Column(db.Integer, db.ForeignKey('cooklists.id', ondelete='CASCADE'))


######### INGREDIENTS #########
class Ingredient(db.Model):
    '''Favorite recipes ingredient table'''
    __tablename__ = "ingredients"

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id    = db.Column(db.String(50), db.ForeignKey('recipes.id', ondelete='CASCADE'))
    name         = db.Column(db.String(150), nullable=False)
    aisle        = db.Column(db.String(50), nullable=True)
    image        = db.Column(db.String(150), nullable=True)
    metric_unit  = db.Column(db.String(50), nullable=True)
    metric_value = db.Column(db.String(50), nullable=True)
    us_unit      = db.Column(db.String(50), nullable=True)
    us_value     = db.Column(db.String(50), nullable=True)


######### USERS < RECIPES #########
class UserRecipe(db.Model):
    """Mapping of a playlist to a song."""

    __tablename__ = "user_recipe"
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id     = db.Column(db.Integer,    db.ForeignKey('users.id'))
    recipe_id   = db.Column(db.String(50), db.ForeignKey('recipes.id'))



######### USERS #########
class User(db.Model):
    '''Users table'''
    __tablename__ = "users"

    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email      = db.Column(db.String(50), nullable=False, unique=True)
    password   = db.Column(db.String(), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name  = db.Column(db.String(30), nullable=True)
    ## Relationships ##
    
    


    def get_full_name(self):
            return f"{self.first_name} {self.last_name}"
    full_name = property(get_full_name)

    @classmethod
    def register(cls, email, password, first_name, last_name):
            hashed = bcrypt.generate_password_hash(password)
            hashed_utf8 = hashed.decode('utf8')
            return cls(email=email, password=hashed_utf8, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, email, password):
            usr = User.query.filter_by(email=email).first()
            if usr and bcrypt.check_password_hash(usr.password, password):
                    return usr
            else:
                    return False


######### USER PREFERENCES #########
class UserPreference(db.Model):
    '''User Preferences table'''
    __tablename__ = "user_preferences"

    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'))
    measure_system = db.Column(db.String(6), nullable=True)


######### INGREDIENTS LIST #########
class IngredientList(db.Model):
    '''List of ingredients table'''
    __tablename__ = "ingredients_list"

    id   = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50), nullable=True)

#### App connect
def connect_db(app):
    db.app = app
    db.init_app(app)
    # db.create_all()
