from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.route('/')
def index():
   return render_template('home.html')


@app.route('/login')
def login():
   return render_template('login.html')


@app.route('/register')
def register():
   return render_template('register.html')


@app.route('/dashboard')
def dashboard():
   return render_template('dashboard.html')


@app.route('/currencies')
def currencies():
   return render_template('cryptocurrencies.html')


@app.route('/watchlist')
def watchlist():
   return render_template('watchlist.html')


@app.route('/transactions')
def transactions():
   return render_template('transactions.html')


if __name__ == '__main__':
   app.run(debug=True)