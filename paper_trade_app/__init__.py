from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import find_dotenv, load_dotenv
from flask_bootstrap import Bootstrap


db = SQLAlchemy()

DB_NAME = 'choco.db'


load_dotenv(find_dotenv())

SECRET_KEY = os.urandom(32)
SQLALCHEMY_DB_URI = os.getenv('DATABASE_URL')

if SQLALCHEMY_DB_URI and SQLALCHEMY_DB_URI.startswith("postgres://"):
    SQLALCHEMY_DB_URI = SQLALCHEMY_DB_URI.replace("postgres://", "postgresql://", 1)


def create_app():
   
   app = Flask(__name__)
   app.config['SECRET_KEY'] = SECRET_KEY

   app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DB_URI
   app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
   db.init_app(app)

   bootstrap = Bootstrap(app)

   from .views import views

   app.register_blueprint(views, url_prefix='/')
   

   from .models import users

   create_db(app)

   login_manager = LoginManager()
   login_manager.login_view = 'views.login'
   login_manager.init_app(app)


   @login_manager.user_loader
   def load_user(id):
      return users.query.get(int(id))

   return app



def create_db(app):
   if not os.path.exists('app/' + DB_NAME):
      db.create_all(app=app)
      print('DB Created')