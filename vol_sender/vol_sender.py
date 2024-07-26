import time
import requests
import json

def fetch_data():
    end_time = int(time.time()) * 1000
    start_time = end_time - 24 * 60 * 60 * 1000
    url = f"https://mizar-gateway.signalplus.net/mizar/iv?exchange=deribit&currency=BTC&startTime={start_time}&endTime={end_time}"
    response = requests.get(url)
    print(url)
    print(response)
    data = response.text
    print(data)
    weekly_data = json.loads(data)["value"][2] # [2] is for weekly data
    key_list = " ".join([str(x) for x in weekly_data.keys()])
    print(key_list)
    res = "\t".join([str(x) for x in weekly_data.values()])
    print(res)  # Tim needs this

    return(res)

def send(message):
    print("Sending data...")
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
        print(f"Data send successful with code: {rep.text}")
    except requests.exceptions.ProxyError as e:
        print(f"requests.exceptions.ProxyError {e}, please check your proxy")


def send_vol_data():
    vol_data = fetch_data()
    send(f"Here's the 4pm vol data:\n{vol_data}")

if __name__ == "__main__":
    send_vol_data()