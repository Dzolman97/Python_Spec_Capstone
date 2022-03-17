from . import db
from flask_login import UserMixin
from time import time


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