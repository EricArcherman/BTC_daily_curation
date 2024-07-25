import json
import requests
import pandas as pd

def fetch_data():
    file_path = 'extracted_prices.csv'
    df = pd.read_csv(file_path)

    last_row = df.iloc[-3]
    last_row_str = '\t'.join(map(str, last_row.values))

    return last_row_str

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
        print('lark bot response: ', rep.text)
    except requests.exceptions.ProxyError as e:
        print(f"requests.exceptions.ProxyError {e}, please check your proxy")

if __name__ == "__main__":
    target_message = fetch_data()
    lark_data_loader(f"Here's yesterday's data:\n{target_message}")