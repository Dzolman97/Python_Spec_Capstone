from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import login_required, current_user, logout_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import LoginForm, RegisterForm, WatchlistForm, TransactionForm
from .models import users, user_watchlist, coin_data, transaction_ledger, wallet, cur_investment
from . import db
from datetime import datetime
from time import time



views = Blueprint('views', __name__)


@views.route('/')
def index():
   return render_template('home.html')


@views.route('/login', methods=['GET', 'POST'])
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


@views.route('/register', methods=['GET', 'POST'])
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


@views.route('/dashboard')
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


   coin_totals = []

   for coin in wallet_info:
      for item in user_wallet:
         if coin.id == item.coin_id:
            amount = item.quantity * float(coin.coin_price)
            coin_totals.append(amount)

   current_investment.investment_amount = sum(coin_totals)
   db.session.commit()


   return render_template('dashboard.html', name=current_user.username, watching=list_of_watching, buying_power=current_user.buying_power, current_investment=current_investment.investment_amount, wallet_info=wallet_info, user_wallet=user_wallet)


@views.route('/currencies')
@login_required
def currencies():
   current = coin_data.query.all()
   return render_template('cryptocurrencies.html', current=current)


@views.route('/buypage/coin_id/<int:id>', methods=['GET', 'POST'])
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


@views.route('/sellpage/coin_id/<int:id>', methods=['GET', 'POST'])
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


@views.route('/watchlist', methods=['GET', 'POST'])
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


@views.route('/delete/<int:id>')
def delete(id):
   coin_to_delete = user_watchlist.query.filter_by(coin_id=id).first()

   try:
      db.session.delete(coin_to_delete)
      db.session.commit()
      return redirect(url_for('watchlist'))

   except:
      return "There was a problem deleting this from your watchlist. Please try again later."


@views.route('/transactions')
@login_required
def transactions():
   users_transactions = transaction_ledger.query.filter_by(user_id=current_user.id).all()

   coin_info = []

   for info in users_transactions:
      coin_info_query = coin_data.query.filter_by(id=info.coin_id).first()
      coin_info.append(coin_info_query)

   return render_template('transactions.html', users_transactions=users_transactions, coin_info=coin_info)


@views.route('/signout')
@login_required
def signout():
   logout_user()
   return redirect(url_for('index'))

@views.app_template_filter('to_float')
def to_float_filter(f):
   return float(f)