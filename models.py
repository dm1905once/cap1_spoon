from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


######### RECIPES #########
class Recipe(db.Model):
    '''Recipes table'''
    __tablename__ = "recipes"

    id                = db.Column(db.String(50), primary_key=True)
    title             = db.Column(db.String(250), nullable=False)
    summary           = db.Column(db.String(10480), nullable=True)
    image             = db.Column(db.String(250), nullable=True)
    ready_in_minutes  = db.Column(db.Integer, nullable=True)
    servings          = db.Column(db.Integer, nullable=True)
    instructions      = db.Column(db.JSON, nullable=True)
    ## Relationships ##
    ingredients = db.relationship('Ingredient')
    cooklists   = db.relationship('Cooklist', secondary='cooklists_recipes')

    @classmethod
    def save(cls, id, title, summary, image, ready_in_minutes, servings, instructions, ingredients):
        id=str(id)
        analyzedInstructions = instructions[0]['steps'] if instructions else None  # Some recipes don't have instructions

        new_recipe = cls(id=id, title=title, summary=summary, image=image, ready_in_minutes=ready_in_minutes, servings=servings, instructions=analyzedInstructions)
        db.session.add(new_recipe)

        # Save recipe ingredients in ingredients table
        for ingredient in ingredients:
            new_ingredient = Ingredient(
                recipe_id   = id,
                name        = ingredient['name'],
                aisle       = ingredient['aisle'],
                image       = ingredient['image'],
                metric_unit = ingredient['measures']['metric']['unitLong'],
                metric_value = ingredient['measures']['metric']['amount'],
                us_unit     = ingredient['measures']['us']['unitLong'],
                us_value    = ingredient['measures']['us']['amount']
                )
            db.session.add(new_ingredient)
        
        db.session.commit()
        return new_recipe


######### COOKLISTS #########
class Cooklist(db.Model):
    '''Cooklist table. Like Playlists, but for cooking'''
    __tablename__ = "cooklists"

    id           = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    list_name    = db.Column(db.String(50), nullable=False, unique=True)
    description  = db.Column(db.String(250), nullable=True)
    created_date = db.Column(db.DateTime, nullable=False)
    ## Relationships ##
    recipes   = db.relationship('Recipe', secondary='cooklists_recipes')

    def print_created_date(self):
        return print_datetime(self.created_date)

    ## Properties ##
    created_date_readable = property(print_created_date)


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
    preferences = db.relationship('UserPreference', uselist=False)
    favorites   = db.relationship('Recipe', secondary='user_recipe')
    cooklists   = db.relationship('Cooklist')
    


    def get_full_name(self):
            return f"{self.first_name} {self.last_name}"
    full_name = property(get_full_name)

    @classmethod
    def register(cls, email, password, first_name, last_name, measure_system):
            hashed = bcrypt.generate_password_hash(password)
            hashed_utf8 = hashed.decode('utf8')
            return cls(email=email, password=hashed_utf8, first_name=first_name, last_name=last_name, preferences=UserPreference(measure_system=measure_system))

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

def print_datetime(some_datetime):
    return f"{some_datetime.strftime('%c')}"