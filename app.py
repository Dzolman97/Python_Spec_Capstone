from datetime import datetime
from time import time
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
# --------------------------  Database Classes  ------------------------------
# --------- Note to self, put these in seperate folder when ready. -----------
class coin_data(db.Model):
   coin_keys = db.Column(db.Integer, primary_key=True)
   coin_name = db.Column(db.String, nullable=False)
   coin_symbol = db.Column(db.String, nullable=False)
   coin_price = db.Column(db.Float(14, 5), nullable=False)
   market_cap = db.Column(db.Float(14, 5), nullable=False)
   volume_24h = db.Column(db.Float(14, 5), nullable=False)
   volume_change_24h = db.Column(db.Float, nullable=False)
   percent_change_1h = db.Column(db.Float, nullable=False)
   percent_change_24h = db.Column(db.Float, nullable=False)
   percent_change_7d = db.Column(db.Float, nullable=False)
   percent_change_30d = db.Column(db.Float, nullable=False)
   percent_change_60d = db.Column(db.Float, nullable=False)
   percent_change_90d = db.Column(db.Float, nullable=False)
   time = db.Column(db.TIMESTAMP, nullable=False)

   def __init__(self, coin_keys, coin_name, coin_symbol, coin_price, market_cap, volume_24h, volume_change_24h, percent_change_1h, percent_change_24h, percent_change_7d, percent_change_30d, percent_change_60d, percent_change_90d):
      self.coin_keys = coin_keys
      self.coin_name = coin_name
      self.coin_symbol = coin_symbol
      self.coin_price = coin_price
      self.market_cap = market_cap
      self.volume_24h = volume_24h
      self.volume_change_24h = volume_change_24h
      self.percent_change_1h = percent_change_1h
      self.percent_change_24h =percent_change_24h
      self.percent_change_7d = percent_change_7d
      self.percent_change_30d = percent_change_30d
      self.percent_change_60d = percent_change_60d
      self.percent_change_90d = percent_change_90d
      self.time = time

class users(UserMixin ,db.Model):
   id = db.Column(db.Integer, primary_key=True)
   email = db.Column(db.String(300), nullable=False, unique=True)
   password = db.Column(db.String(300), nullable=False)
   username = db.Column(db.String(75), nullable=False, unique=True)
   starting_dollars = db.Column(db.Float(14, 5), nullable=False)
   buying_power = db.Column(db.Float(14, 5))

   def __init__(self, email, password, username, starting_dollars):
      self.email = email
      self.password = password
      self.username = username
      self.starting_dollars = starting_dollars

@lm.user_loader
def load_user(id):
   return users.query.get(int(id))


# -------------------  Login and Register Form Classes -----------------------
# --------- Note to self, put these in seperate folder when ready. -----------


class LoginForm(FlaskForm):
   username = StringField('Username:', validators=[InputRequired(), Length(min=5, max=20)])
   password = PasswordField('Password:', validators=[InputRequired(), Length(min=8, max=80)])


class RegisterForm(FlaskForm):
   email = StringField('Email:', validators=[Email(message="Valid email required"), Length(max=55)])
   username = StringField('Username:', validators=[InputRequired(), Length(min=5, max=20)])
   password = PasswordField('Password:', validators=[InputRequired(), Length(min=8, max=80)])
   starting_dollars = StringField('How much money do you want to start with?', validators=[InputRequired(), Length(min=4)])


# -----------   Routes   --------------


@app.route('/')
def index():
   return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
   form = LoginForm()

   if form.validate_on_submit():
      user = users.query.filter_by(username=form.username.data).first()
      if user:
         if check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))

      return '<h1> Invalid username or password. </h1>'


   return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
   form = RegisterForm()

   if form.validate_on_submit():
      starting_dollars = int(form.starting_dollars.data)
      hashed_pass = generate_password_hash(form.password.data, method='sha256')
      new_user = users(email=form.email.data, username=form.username.data, password=hashed_pass, starting_dollars=starting_dollars)
      db.session.add(new_user)
      db.session.commit()

      return "<h1> New User has been Created </h1>"

   return render_template('register.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
   return render_template('dashboard.html', name=current_user.username)


@app.route('/currencies')
@login_required
def currencies():
   current = coin_data.query.all()
   return render_template('cryptocurrencies.html', current=current)


@app.route('/watchlist')
@login_required
def watchlist():
   return render_template('watchlist.html')


@app.route('/transactions')
@login_required
def transactions():
   return render_template('transactions.html')


@app.route('/signout')
@login_required
def signout():
   logout_user()
   return redirect(url_for('index'))


if __name__ == '__main__':
   db.create_all()
   app.run(debug=True)