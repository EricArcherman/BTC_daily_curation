import json

import numpy as np
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz


def is_hour(ts):
    return ts % (1000 * 3600) == 0


def fetch_data():
    file_path = 'extracted_prices.csv'
    df = pd.read_csv(file_path)

    yesterday, today = df.iloc[-2], df.iloc[-1]

    yesterday_formatted = '\t'.join(map(str, yesterday.values))
    today_formatted = '\t'.join(map(str, today.values))

    return yesterday_formatted, today_formatted


def lark_data_loader(message):
    try:
        payload_message = {
            "msg_type": "text",
            "content": {
                "text": message
            }
        }
        webhook_adr = 'https://open.larksuite.com/open-apis/bot/v2/hook/23d73fed-e7df-470c-ad9f-a07a24a17d77'
        headers = {'Content-Type': 'application/json'}
        rep = requests.post(url=webhook_adr, data=json.dumps(payload_message), headers=headers)
        print('Message send successful, finished with code: ', rep.text)
    except requests.exceptions.ProxyError as e:
        print(f"requests.exceptions.ProxyError {e}, please check your proxy")


def yesterday_data():
    # 获取当前时间
    now = datetime.now()
    # 设置时区为UTC+8
    utc8 = pytz.timezone('Asia/Shanghai')

    # 将当前时间转换为UTC+8时区时间
    now_utc8 = utc8.localize(now)

    # 获取当天的0点时间戳
    midnight_utc8 = utc8.localize(datetime(now_utc8.year, now_utc8.month, now_utc8.day))

    # 获取前一天的0点时间戳
    yesterday_midnight_utc8 = midnight_utc8 - timedelta(days=1)
    yesterday_date = yesterday_midnight_utc8.date()

    # 将时间转换为时间戳
    midnight_timestamp = int(midnight_utc8.timestamp()) * 1000
    yesterday_midnight_timestamp = int(yesterday_midnight_utc8.timestamp()) * 1000

    start_time = yesterday_midnight_timestamp - 1000
    end_time = midnight_timestamp - 1000
    url = f"https://mizar-gateway.signalplus.net/mizar/index_price?exchange=deribit&currency=BTC&startTime={start_time}&endTime={end_time}"
    res = requests.get(url).json()
    res_dict = pd.DataFrame(res["value"])
    is_hour_list = res_dict["timestamp"].apply(lambda x: is_hour(x))
    res_dict = res_dict.loc[is_hour_list, :].reset_index(drop=True)
    data_message = '\t'.join(
        map(str, list(res_dict["indexPrice"].values) + [np.nan] * (24 - len(res_dict["indexPrice"].values))))
    full_message = f"Here's yesterday's data:\n{yesterday_date}\t{data_message}"
    print(full_message)
    lark_data_loader(f"{full_message}")


def today_data():
    # 获取当前时间
    now = datetime.now()
    current_date = datetime.now().date()
    # 设置时区为UTC+8
    utc8 = pytz.timezone('Asia/Shanghai')

    # 将当前时间转换为UTC+8时区时间
    now_utc8 = utc8.localize(now)

    # 获取当天的0点时间戳
    midnight_utc8 = utc8.localize(datetime(now_utc8.year, now_utc8.month, now_utc8.day))

    # 获取当天的10点时间戳
    ten_am_utc8 = midnight_utc8.replace(hour=10)

    # 获取前一天的0点时间戳
    yesterday_midnight_utc8 = midnight_utc8 - timedelta(days=1)

    # 将时间转换为时间戳
    midnight_timestamp = int(midnight_utc8.timestamp()) * 1000
    ten_am_timestamp = int(ten_am_utc8.timestamp()) * 1000

    start_time = midnight_timestamp - 1000
    end_time = ten_am_timestamp + 1000
    url = f"https://mizar-gateway.signalplus.net/mizar/index_price?exchange=deribit&currency=BTC&startTime={start_time}&endTime={end_time}"
    res = requests.get(url).json()
    res_dict = pd.DataFrame(res["value"])
    is_hour_list = res_dict["timestamp"].apply(lambda x: is_hour(x))
    res_dict = res_dict.loc[is_hour_list, :].reset_index(drop=True)
    data_message = '\t'.join(
        map(str, list(res_dict["indexPrice"].values) + [np.nan] * (24 - len(res_dict["indexPrice"].values))))
    full_message = f"Here's today's data:\n{current_date}\t{data_message}"
    print(full_message)
    lark_data_loader(full_message)


if __name__ == "__main__":
    today_data()
