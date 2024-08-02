import json
import requests
import pandas as pd

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
    target_message = fetch_data()
    lark_data_loader(f"Here's yesterday's data:\n{target_message[0]}")

def today_data():
    target_message = fetch_data()
    lark_data_loader(f"Here's today's data:\n{target_message[1]}")

if __name__ == "__main__":
    today_data()