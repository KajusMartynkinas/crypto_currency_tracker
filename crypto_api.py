import os
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
from time import sleep
import seaborn as sns
import matplotlib.pyplot as plt


df = pd.DataFrame()

# Running the API runner multiple times
for i in range(10):
  url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
  parameters = {
    'start': '1',
    'limit': '15',
    'convert': 'USD'
  }
  headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '34bb1490-0c90-484a-835a-d7ecbee4b658',
  }

  session = Session()
  session.headers.update(headers)

  try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    df2 = pd.json_normalize(data['data'])
    df2['timestamp'] = pd.to_datetime('now', utc=True)

    # Concatenate df2 to the global df DataFrame
    index = pd.Index(range(120))

    df = pd.concat([df, df2], ignore_index=True)
    df3 = df.groupby('name', sort=False)[['quote.USD.percent_change_1h','quote.USD.percent_change_24h', 'quote.USD.percent_change_7d',
                                    'quote.USD.percent_change_30d', 'quote.USD.percent_change_60d', 'quote.USD.percent_change_90d']].mean()
    df4 = df3.stack()
    df5 = df4.to_frame(name='values')
    df6 = df5.reset_index()
    df7 = df6.rename(columns = {'level_1': 'percent_change'})
    df7['percent_change'] = df7['percent_change'].replace(['quote.USD.percent_change_1h', 'quote.USD.percent_change_24h','quote.USD.percent_change_7d',
                                         'quote.USD.percent_change_30d', 'quote.USD.percent_change_60d', 'quote.USD.percent_change_90d'],
                                        ['1h','24h','7d','30d','60d','90d'])

    df_bitcoin = df[['name','quote.USD.price', 'timestamp']]
    df_bitcoin = df_bitcoin.query("name == 'Bitcoin'")


  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)

  # Set display options
  pd.set_option('display.max_columns', None)
  pd.set_option('display.max_rows', None)
  pd.set_option('display.width', None)
  pd.set_option('display.float_format', lambda x: '%.5f' % x)

  def catplot():
    plt.style.use('dark_background')
    sns.catplot(x='percent_change', y ='values', hue = 'name', data = df7, kind = 'point')
    plt.show()

  def lineplot():
    sns.set_theme(style='darkgrid')
    sns.lineplot(x='timestamp', y='quote.USD.price', data = df_bitcoin)
    plt.show()
  print(df_bitcoin)

  # if not os.path.isfile(r'C:\Users\Aero\Documents\GitHub\crypto_api\CryptoMarket.csv'):
  #   df5.to_csv('CryptoMarket.csv', header='column_names')
  # else:
  #   df5.to_csv('CryptoMarket.csv', mode='a', header=False)

  print('API runner completed')
  sleep(5)

print('1. Top 15 cryptocurrency price changes')
print('2. Bitcoin price changes')
print('0. Exit program')
choice = input('Choose which graph you wish to see:\n')
if choice == '1':
  catplot()
elif choice == '2':
  lineplot()
elif choice == '0':
  exit()
else:
  print('Incorrect number')

exit()