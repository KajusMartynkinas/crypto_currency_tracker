import os
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
from time import sleep


# Initialize df as an empty DataFrame globally
df = pd.DataFrame()

def api_runner():
  global df
  url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
  parameters = {
    'start': '1',
    'limit': '20',
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

  except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)

  # Set display options
  pd.set_option('display.max_columns', None)
  pd.set_option('display.max_rows', None)
  pd.set_option('display.width', None)
  pd.set_option('display.float_format', lambda x: '%.5f' % x)



  # Export to CSV
  print(df7)

  # if not os.path.isfile(r'C:\Users\Aero\PycharmProjects\pythonProject2\CryptoMarket.csv'):
  #   df5.to_csv('CryptoMarket.csv', header='column_names')
  # else:
  #   df5.to_csv('CryptoMarket.csv', mode='a', header=False)

# Running the API runner multiple times
for i in range(1):
  api_runner()
  print('API runner completed')
  sleep(60)

exit()