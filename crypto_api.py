import os
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
from time import sleep
import seaborn as sns
import matplotlib.pyplot as plt


# Initialize df as an empty DataFrame globally
df = pd.DataFrame()

def api_runner():
  global df
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

    df8 = df[['name','quote.USD.price', 'timestamp']]
    df8 = df8.query("name == 'Bitcoin'")


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
    sns.lineplot(x='timestamp', y='quote.USD.price', data = df8)
  # Export to CSV
  print(df8)

  # if not os.path.isfile(r'C:\Users\Aero\PycharmProjects\pythonProject2\CryptoMarket.csv'):
  #   df5.to_csv('CryptoMarket.csv', header='column_names')
  # else:
  #   df5.to_csv('CryptoMarket.csv', mode='a', header=False)

# Running the API runner multiple times
for i in range(3):
  api_runner()
  print('API runner completed')
  sleep(10)
exit()