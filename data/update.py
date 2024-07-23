import time
import requests
import json
import pandas as pd
from datetime import datetime

RUNNING = 'data/running-2-years.csv'
EXCHANGE = 'deribit'
CURRENCY = 'BTC'
LAST_UPDATE = 69 # just an initialization variable, (teehee!)

def update(running, exchange, currency):
    print(f"Reading file: {running}")
    data = pd.read_csv(running)

    print(f"Calculating API fetch bounds")
    last_record = data['timestamp'].iloc[-1]
    current = round(time.time() / 60) * 60000

    start_timestamp = last_record + 60000 # avoid duplicates
    end_timestamp = current - 60000 # database lag
    url = f"https://mizar-gateway.signalplus.net/mizar/index_price?exchange={exchange}&currency={currency}&startTime={start_timestamp}&endTime={end_timestamp}"

    LAST_UPDATE = datetime.fromtimestamp(end_timestamp / 1000)

    print(f"Fetching recent prices from database @ {url}")
    res = requests.get(url=url)
    
    try:
        latest = json.loads(res.text)["value"]
        print(f"Prices received.")
    except ValueError as e:
        print("Data is already up to date! We're just updating an empty dataframe.")
        latest = {'timestamp', 'indexPrice'}

    print(f"Updating {running}")
    latest_prices = pd.DataFrame(latest)

    new_data = pd.concat([data, latest_prices], ignore_index=True)

    two_years = 2*365*24*60
    new_data = new_data.iloc[-two_years:]

    print(f"Writing to {running}")
    new_data.to_csv(running, index=False)

    print(f"{running} successfully last updated at {LAST_UPDATE}.")


if __name__ == "__main__":
    update(RUNNING, EXCHANGE, CURRENCY)
    print("Program done!")