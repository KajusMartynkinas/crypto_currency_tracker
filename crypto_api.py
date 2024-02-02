import os
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
from time import sleep
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



df = pd.DataFrame()
number = int(input('Choose how many times you wish to reload the data: \n'))
time = int(input('Choose how often you wish the reload to happen (seconds): \n'))

# Running the API runner multiple times
for i in range(number):
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
    plt.gcf().autofmt_xdate()  # Automatically format the x-axis labels to fit better
    plt.gca().xaxis.set_major_locator(
      mdates.AutoDateLocator())  # Use the AutoDateLocator to choose the date interval intelligently
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # Format the date to show only hour and minute
    plt.xticks(rotation=45, ha='right')
    plt.show()
  print(df_bitcoin)
  print(df7)

  current_directory = os.getcwd()
  top15_crypto_file = os.path.join(current_directory, 'top15_crypto.csv')
  bitcoin_file = os.path.join(current_directory, 'bitcoin.csv')

  # Check for 'top15_crypto.csv' and write to it
  if not os.path.isfile(top15_crypto_file):
    df7.to_csv(top15_crypto_file, header=True)
  else:
    df7.to_csv(top15_crypto_file, mode='a', header=False, index=False)

  # Check for 'bitcoin.csv' and write to it
  if not os.path.isfile(bitcoin_file):
    df_bitcoin.to_csv(bitcoin_file, header=True)
  else:
    df_bitcoin.to_csv(bitcoin_file, mode='a', header=False, index=False)

  catplot()
  lineplot()
  print('API runner completed')
  sleep(time)

print('Process finished')
exit()