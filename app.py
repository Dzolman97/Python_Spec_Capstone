from datetime import datetime
from time import time
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


# --------------------------  Database Classes  ------------------------------
# --------- Note to self, put these in seperate files when ready. -----------


class coin_data(db.Model):
   id = db.Column(db.Integer, primary_key=True)
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

   def __init__(self, coin_name, coin_symbol, coin_price, market_cap, volume_24h, volume_change_24h, percent_change_1h, percent_change_24h, percent_change_7d, percent_change_30d, percent_change_60d, percent_change_90d):
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

   def __init__(self, email, password, username, starting_dollars, buying_power):
      self.email = email
      self.password = password
      self.username = username
      self.starting_dollars = starting_dollars
      self.buying_power = buying_power

class user_watchlist(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
   coin_id = db.Column(db.Integer, db.ForeignKey('coin_data.id'))

class transaction_ledger(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
   coin_id = db.Column(db.Integer, db.ForeignKey('coin_data.id'))
   buy = db.Column(db.Boolean, nullable=False)
   sell = db.Column(db.Boolean, nullable=False)
   quantity = db.Column(db.Float)
   price_at_transaction = db.Column(db.Float)
   transaction_in_dollars = db.Column(db.Float)
   time = db.Column(db.TIMESTAMP)

class wallet(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
   coin_id = db.Column(db.Integer, db.ForeignKey('coin_data.id'))
   quantity = db.Column(db.Float)

class cur_investment(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
   investment_amount = db.Column(db.Float)
   time = db.Column(db.TIMESTAMP)


@lm.user_loader
def load_user(id):
   return users.query.get(int(id))


# -------------------  Login and Register Form Classes -----------------------
# --------- Note to self, put these in seperate files when ready. -----------


class LoginForm(FlaskForm):
   username = StringField('Username:', validators=[InputRequired(), Length(min=5, max=20)])
   password = PasswordField('Password:', validators=[InputRequired(), Length(min=8, max=80)])


class RegisterForm(FlaskForm):
   email = StringField('Email:', validators=[Email(message="Valid email required"), Length(max=55)])
   username = StringField('Username:', validators=[InputRequired(), Length(min=5, max=20)])
   password = PasswordField('Password:', validators=[InputRequired(), Length(min=8, max=80)])
   starting_dollars = StringField('How much money do you want to start with?', validators=[InputRequired(), Length(min=4)])


class WatchlistForm(FlaskForm):
   coin_name = StringField('Search for a Coin to add to your watchlist:', validators=[InputRequired()])


class TransactionForm(FlaskForm):
   dollar_amnt = StringField('Transaction Amount in Dollars: ', validators=[InputRequired(), Length(min=1)])


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

      flash("Invalid username or password.")
      return render_template('login.html', form=form)


   return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
   form = RegisterForm()

   if form.validate_on_submit():
      starting_dollars = int(form.starting_dollars.data)
      hashed_pass = generate_password_hash(form.password.data, method='sha256')
      new_user = users(email=form.email.data, username=form.username.data, password=hashed_pass, starting_dollars=starting_dollars, buying_power=starting_dollars)
      db.session.add(new_user)
      db.session.commit()

      flash("New user successfully created! Please Login!")
      return redirect(url_for('login'))

   return render_template('register.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
   u_id = current_user.id
   user_watching_these = user_watchlist.query.filter_by(user_id=u_id).all()
   list_of_watching = []
   for coin in user_watching_these:
      coin_id = coin.coin_id
      query_data = coin_data.query.get(coin_id)
      list_of_watching.append(query_data)
   
   cur_investment_exists = cur_investment.query.filter_by(user_id=u_id).first()

   if cur_investment_exists == None or cur_investment_exists == False:
      create_cur_investment = cur_investment(user_id=u_id, investment_amount=0, time=datetime.now())
      db.session.add(create_cur_investment)
      db.session.commit()
   else:
      pass
   
   current_investment = cur_investment.query.filter_by(user_id=u_id).first()
   user_wallet = wallet.query.filter_by(user_id=u_id).all()

   wallet_info = []

   for coin in user_wallet:
      coin_info = coin_data.query.filter_by(id=coin.coin_id).first()
      wallet_info.append(coin_info)

   return render_template('dashboard.html', name=current_user.username, watching=list_of_watching, buying_power=current_user.buying_power, current_investment=current_investment.investment_amount, wallet_info=wallet_info, user_wallet=user_wallet)


@app.route('/currencies')
@login_required
def currencies():
   current = coin_data.query.all()
   return render_template('cryptocurrencies.html', current=current)


@app.route('/buypage/coin_id/<int:id>', methods=['GET', 'POST'])
@login_required
def buypage(id):

   coin_info = coin_data.query.filter_by(id=id)
   coin_price = []

   for i in coin_info:
      price = i.coin_price
      coin_price.append(price)

   form = TransactionForm()

   if request.method == 'POST':

      if form.validate_on_submit():

         dollar_amnt = float(int(form.dollar_amnt.data))
         buy_quantity = float(dollar_amnt / float(coin_price[0]))
         in_wallet = wallet.query.filter_by(user_id=current_user.id, coin_id=id).first()
         user = users.query.get(current_user.id)
         dt = datetime.now()

         if user.buying_power >= dollar_amnt:

            if in_wallet == None or in_wallet == 0:
               new_transaction = transaction_ledger(user_id=current_user.id, coin_id=id, buy=True, sell=False, quantity=buy_quantity, price_at_transaction=float(coin_price[0]), transaction_in_dollars=dollar_amnt, time=dt)
               wallet_addition = wallet(user_id=current_user.id, coin_id=id, quantity=buy_quantity)
               user.buying_power = int(user.buying_power) - dollar_amnt
               current_investment = cur_investment.query.filter_by(user_id=user.id).first()
               current_investment.investment_amount = int(current_investment.investment_amount) + dollar_amnt
               db.session.add(new_transaction)
               db.session.add(wallet_addition)
               db.session.commit()
               return redirect('/dashboard')
            
            elif in_wallet.quantity >= 0:
               new_transaction = transaction_ledger(user_id=current_user.id, coin_id=id, buy=True, sell=False, quantity=buy_quantity, price_at_transaction=float(coin_price[0]), transaction_in_dollars=dollar_amnt, time=dt)
               in_wallet.quantity += buy_quantity
               user.buying_power = int(user.buying_power) - dollar_amnt
               current_investment = cur_investment.query.filter_by(user_id=user.id).first()
               current_investment.investment_amount = int(current_investment.investment_amount) + dollar_amnt
               db.session.add(new_transaction)
               db.session.commit()
               return redirect('/dashboard')

            else:
               return "here"

         else:
            flash(f"You do not have enough buying power. The max you can buy is ${float(user.buying_power)}")
            return redirect(f'/buypage/coin_id/{id}')

      else:
         return "oops!"

   elif request.method == 'GET':
      return render_template('buypage.html', form=form, info=coin_info, price=coin_price[0])


@app.route('/sellpage/coin_id/<int:id>', methods=['GET', 'POST'])
@login_required
def sellpage(id):

   coin_info = coin_data.query.filter_by(id=id)
   coin_price = []
   
   for i in coin_info:
      price = i.coin_price
      coin_price.append(price)
   form = TransactionForm()

   if request.method == 'POST':

      if form.validate_on_submit():

         dollar_amnt = float(int(form.dollar_amnt.data))
         sell_quantity = float(dollar_amnt / float(coin_price[0]))
         in_wallet = wallet.query.filter_by(user_id=current_user.id, coin_id=id).first()
         dt = datetime.now()

         if in_wallet == None or in_wallet == 0:
            flash("You don't own any of this currecy.")
            return redirect(f'/sellpage/coin_id/{id}')

         elif in_wallet.quantity > 0:

            if in_wallet.quantity - sell_quantity >= 0:
               in_wallet.quantity -= sell_quantity
               new_transaction = transaction_ledger(user_id=current_user.id, coin_id=id, buy=False, sell=True, quantity=sell_quantity, price_at_transaction=float(coin_price[0]), transaction_in_dollars=dollar_amnt, time=dt)
               user = users.query.get(current_user.id)
               user.buying_power = int(user.buying_power) + dollar_amnt
               current_investment = cur_investment.query.filter_by(user_id=user.id).first()
               current_investment.investment_amount = int(current_investment.investment_amount) - dollar_amnt
               db.session.add(new_transaction)
               db.session.commit()
               if in_wallet.quantity == 0:
                  wallet.query.filter_by(user_id=current_user.id, coin_id=id).delete()
                  db.session.commit()
                  pass
               return redirect(url_for('dashboard'))
            
            else:
               max_sell_amount = int(in_wallet.quantity) * coin_price[0]
               flash(f"Your max sell amount is ${max_sell_amount}")
               return redirect(f'/sellpage/coin_id/{id}')

         else:
            flash("You don't own any of this currecy.")
            return redirect(f'/sellpage/coin_id/{id}')

      else:
         return "oops!"

   elif request.method == 'GET':
      return render_template('sellpage.html', form=form, info=coin_info, price=coin_price[0])


@app.route('/watchlist', methods=['GET', 'POST'])
def watchlist():
   form = WatchlistForm()
   u_id = current_user.id

   if request.method == 'POST':
      if form.validate_on_submit():
         coin_name = form.coin_name.data
         if coin_name.isupper() == True:
            searched_for = coin_data.query.filter_by(coin_symbol=coin_name).first()
            to_add = user_watchlist(user_id=u_id, coin_id=searched_for.id)
            db.session.add(to_add)
            db.session.commit()
            return redirect(url_for('watchlist'))
         else:
            coin_name = coin_name.capitalize()
            searched_for = coin_data.query.filter_by(coin_name=coin_name).first()
            to_add = user_watchlist(user_id=u_id, coin_id=searched_for.id)
            db.session.add(to_add)
            db.session.commit()
            return redirect(url_for('watchlist'))
   elif request.method == 'GET':
      user_watching_these = user_watchlist.query.filter_by(user_id=u_id).all()
      list_of_watching = []
      for coin in user_watching_these:
         coin_id = coin.coin_id
         query_data = coin_data.query.get(coin_id)
         list_of_watching.append(query_data)
      return render_template('watchlist.html', form=form, watching=list_of_watching, in_watchlist=user_watching_these)


@app.route('/delete/<int:id>')
def delete(id):
   coin_to_delete = user_watchlist.query.filter_by(coin_id=id).first()

   try:
      db.session.delete(coin_to_delete)
      db.session.commit()
      return redirect(url_for('watchlist'))

   except:
      return "There was a problem deleting this from your watchlist. Please try again later."


@app.route('/transactions')
@login_required
def transactions():
   users_transactions = transaction_ledger.query.filter_by(user_id=current_user.id).all()

   coin_info = []

   for info in users_transactions:
      coin_info_query = coin_data.query.filter_by(id=info.coin_id).first()
      coin_info.append(coin_info_query)

   return render_template('transactions.html', users_transactions=users_transactions, coin_info=coin_info)


@app.route('/signout')
@login_required
def signout():
   logout_user()
   return redirect(url_for('index'))

@app.template_filter('to_float')
def to_float_filter(f):
   return float(f)

if __name__ == '__main__':
   db.create_all()
   app.run()