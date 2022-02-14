from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
   return render_template('home.html')


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