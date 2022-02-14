from pprint import pprint
from requests import Request, Session
from requests. exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import psycopg2
from psycopg2.extras import execute_batch
import datetime
import time
import os


# Request specific coins on coin marketcap
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
parameters = {
  'symbol':'BTC,ETH,BNB,DOGE,ETC,LTC,BCH,BSV,ADA,SOL,LUNA,DOT,AVAX,SHIB,BUSD,MATIC,CRO,WBTC,ATOM,LINK,NEAR,UNI,ALGO,TRX,FTT,MANA,FTM,XLM,ICP,HBAR',
  'convert':'USD'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': '',
}

session = Session()
session.headers.update(headers)

res_data = []

try:
  response = session.get(url, params=parameters)
  data = json.loads(response.text)
  res_data.append(data)
except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)

# Callback function to use in getting the latest data
def get_coins():
   return res_data

# Get the latest data
def latest_data():
    listed_coins = get_coins()

    out_of_list = listed_coins[0]['data']
    
    # To be a new list of Dictionaires with data needed
    latest_coin_data = []
    
    # For loop to extract data needed/wanted
    for coin in out_of_list:
       filtered_coin_data = {}

       data = out_of_list[coin]

       filtered_coin_data['coin_name'] = data['name']
       filtered_coin_data['coin_symbol'] = data['symbol']
       filtered_coin_data['coin_price'] = data['quote']['USD']['price']
       filtered_coin_data['market_cap'] = data['quote']['USD']['market_cap']
       filtered_coin_data['volume_24h'] = data['quote']['USD']['volume_24h']
       filtered_coin_data['volume_change_24h'] = data['quote']['USD']['volume_change_24h']
       filtered_coin_data['percent_change_1h'] = data['quote']['USD']['percent_change_1h']
       filtered_coin_data['percent_change_24h'] = data['quote']['USD']['percent_change_24h']
       filtered_coin_data['percent_change_7d'] = data['quote']['USD']['percent_change_7d']
       filtered_coin_data['percent_change_30d'] = data['quote']['USD']['percent_change_30d']
       filtered_coin_data['percent_change_60d'] = data['quote']['USD']['percent_change_60d']
       filtered_coin_data['percent_change_90d'] = data['quote']['USD']['percent_change_90d']
       filtered_coin_data['date'] = datetime.date.today()
       filtered_coin_data['time'] = data['quote']['USD']['last_updated']
       
       # Adding to list of dictionaries each time the loop runs. Expected out: new_list = [{dictionary}, {dictionary}, {dictionary}]
       latest_coin_data.append(filtered_coin_data)

    return latest_coin_data


hostname = ''
database = ''
username = ''
pwd = ''
port_id = 5432
conn = None
cur = None

# To collect and save pricing data. With date and time being saved a map or graph can eventually be made for visualization and backtesting.

try:
  conn = psycopg2.connect(
              host = hostname,
              dbname = database,
              user = username,
              password = pwd,
               port = port_id)
      
  cur = conn.cursor()
      
  #Bulk insert into database
  values = latest_data()
  query = """INSERT INTO latest_coin_data VALUES (%(coin_name)s, %(coin_symbol)s, %(coin_price)s, %(market_cap)s,
          %(volume_24h)s, %(volume_change_24h)s, %(percent_change_1h)s, %(percent_change_24h)s, %(percent_change_7d)s, 
          %(percent_change_30d)s, %(percent_change_60d)s, %(percent_change_90d)s, %(date)s, %(time)s)"""
      
  execute_batch(cur, query, values)

  # print(cur.execute('SELECT * FROM latest_coin_data ORDER BY time DESC;'))

  conn.commit()
except Exception as error:
  print(error)
finally:
  if cur is not None:
      cur.close()
  if conn is not None:
      conn.close()
print("Added data, adding more in 5 minutes...")



while(True):
  time.sleep(300)
  os.system('python get_coin_data.py')