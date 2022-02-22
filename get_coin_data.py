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
  'X-CMC_PRO_API_KEY': os.environ.get('COIN_API_KEY'),
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

    primary_key = 1
    
    # To be a new list of Dictionaires with data needed
    latest_coin_data = []
    
    # For loop to extract data needed/wanted
    for coin in out_of_list:
       filtered_coin_data = {}

       data = out_of_list[coin]

       filtered_coin_data['id'] = primary_key
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
       filtered_coin_data['time'] = data['quote']['USD']['last_updated']
       

       primary_key += 1

       # Adding to list of dictionaries each time the loop runs. Expected out: new_list = [{dictionary}, {dictionary}, {dictionary}]
       latest_coin_data.append(filtered_coin_data)

    return latest_coin_data


hostname = 'localhost'
database = 'test'
username = 'postgres'
pwd = os.environ.get('DB_PASS')
port_id = 5432
conn = None
cur = None

# To collect and save pricing data. With date and time being saved a map or graph can eventually be made for visualization and backtesting.
def initialize_table():
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
    query = """INSERT INTO coin_data VALUES (%(coin_keys)s, %(coin_name)s, %(coin_symbol)s, %(coin_price)s, %(market_cap)s,
            %(volume_24h)s, %(volume_change_24h)s, %(percent_change_1h)s, %(percent_change_24h)s, %(percent_change_7d)s, 
            %(percent_change_30d)s, %(percent_change_60d)s, %(percent_change_90d)s, %(time)s)"""

    execute_batch(cur, query, values)


    conn.commit()
  except Exception as error:
    print(error)
  finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
  print("Initialized table...")


def update_table():
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

    query = """UPDATE coin_data SET coin_price = %(coin_price)s, market_cap = %(market_cap)s, volume_24h = %(volume_24h)s, volume_change_24h = %(volume_change_24h)s,
              percent_change_1h = %(percent_change_1h)s, percent_change_24h = %(percent_change_24h)s, percent_change_7d = %(percent_change_7d)s,
              percent_change_30d = %(percent_change_30d)s, percent_change_60d = %(percent_change_60d)s, percent_change_90d = %(percent_change_90d)s, time = %(time)s
              WHERE id = %(id)s"""
        
    execute_batch(cur, query, values)


    conn.commit()
  except Exception as error:
    print(error)
  finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
  print("Added data, adding more in 5 minutes...")


# initialize_table()

# while(True):
#   time.sleep(300)

update_table()