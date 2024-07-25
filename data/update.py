import time
import requests
import json
import pandas as pd
from datetime import datetime

RUNNING = 'data/running-2-years.csv'
EXCHANGE = 'deribit'
CURRENCY = 'BTC'

def update(running, exchange, currency):
    print(f"Reading file: {running}")
    data = pd.read_csv(running, index_col=False)

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
    except ValueError as e:
        print("Data is already up to date!")
        latest = {'timestamp', 'indexPrice'}
        
        print("Exiting update program...")
        exit()

    print(f"Updating {running}")
    latest_prices = pd.DataFrame(latest)

    new_data = pd.concat([data, latest_prices], ignore_index=True)

    two_years = 2*365*24*60
    new_data = new_data.iloc[-two_years:]

    print(f"Writing to {running}")
    new_data.to_csv(running, index=False)

    print(f"{running} successfully last updated at {LAST_UPDATE}.")


def main():
    update(RUNNING, EXCHANGE, CURRENCY)

if __name__ == "__main__":
    main()
    print("Program done!")