import sqlite3
import random
import re
from flask_user import UserMixin, UserManager
from . import db



tags = db.Table('TaggedDishes',
    db.Column('tag_id', db.Integer, db.ForeignKey('Tag.tag_id'), primary_key=True),
    db.Column('dish_id', db.Integer, db.ForeignKey('dishes.dish_id'), primary_key=True)
)

class Schema:
    def __init__(self):
        self.conn = sqlite3.connect('essensplan.db')
        self.create_dishes_table()
        self.create_days_table()
        self.create_ingredients_table()
        self.create_tags_table()
        self.create_taggedDishes_table()

    def __del__(self):
        # body of destructor
        self.conn.commit()
        self.conn.close()

    def create_dishes_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS "Dishes" (
          dish_id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT,
          countCooked INTEGER,
          tag TEXT,
          lastCooked TEXT
        );
        """
        self.conn.execute(query)

    def create_tags_table(self):

            query = """
            CREATE TABLE IF NOT EXISTS "Tags" (
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
            );
            """
            self.conn.execute(query)

    def create_taggedDishes_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS "TaggedDishes" (
          tag_id INTEGER,
          dish_id INTEGER
        );
        """
        self.conn.execute(query)


    def create_ingredients_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS "Ingredients" (
          dish_id INTEGER,
          name TEXT,
          amount FLOAT,
          unit TEXT
        );
        """
        self.conn.execute(query)

    def create_days_table(self):

        query = """
        CREATE TABLE IF NOT EXISTS "Days" (
          date STRING,
          dish_id INTEGER
        );
        """

        self.conn.execute(query)


# Customize the Register form:
from flask_user.forms import RegisterForm
from wtforms import StringField
from wtforms import validators, ValidationError
from flask_user.translation_utils import lazy_gettext as _    # map _() to lazy_gettext()
class CustomRegisterForm(RegisterForm):
    # Add a country field to the Register form
    first_name = StringField(_('Vorname'), validators=[validators.DataRequired()])
    last_name = StringField(_('Nachname'), validators=[validators.DataRequired()])

# Customize Flask-User
class CustomUserManager(UserManager):

    def customize(self, app):

        # Configure customized forms
        self.RegisterFormClass = CustomRegisterForm
        # NB: assign:  xyz_form = XyzForm   -- the class!
        #   (and not:  xyz_form = XyzForm() -- the instance!)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User Authentication fields
    email = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)


    # User fields
    first_name = db.Column(db.String(50, collation='NOCASE'), nullable=False)
    last_name = db.Column(db.String(50, collation='NOCASE'), nullable=False)
    dishes = db.relationship('Dish', backref='user')
    ingredients = db.relationship('Ingredient', backref='user')
    tags = db.relationship('Tag', backref='user')
    


class Dish(db.Model):
    __tablename__ = 'dishes'
 
    dish_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    countCooked = db.Column(db.Integer)
    note = db.Column(db.String(255))
    created = db.Column(db.DateTime,
                        index=False,
                        unique=False,
                        nullable=False)
    lastCooked = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
        nullable=False)
    ingredients = db.relationship('Ingredient', backref='dishes')
    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
        backref=db.backref('dishes', lazy=True))

       

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Integer)
    unit = db.Column(db.String(255))
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.dish_id'),
        nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
        nullable=False)



class Days(db.Model):
    __tablename__ = 'Days'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    date_as_string = db.Column(db.String(10), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.dish_id'),
        nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
        nullable=False)

class Tag(db.Model):
    __tablename__ = 'Tag'
    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
        nullable=False)

# class Day:
#     def __init__(self, year,month,day, dish_id, hasDish=False, isToday=False):
#         self.date = str(year)+"-"+str(month).zfill(2)+"-"+str(day).zfill(2)
#         self.year = year
#         self.month = month
#         self.day = day
#         self.dish_id = dish_id
#         self.hasDish = hasDish
#         self.isToday = isToday
#         # self.portions = portions