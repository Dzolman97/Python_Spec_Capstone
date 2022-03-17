from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash

# Forms made for ease of use in quick page set up

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