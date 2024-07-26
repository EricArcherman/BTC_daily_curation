from apscheduler.schedulers.blocking import BlockingScheduler
import pytz

from vol_sender.vol_sender import send_vol_data
from data.update import main as update_data
from extract import main as extract_data
from sender.lark_text import main as send_data

send_vol_time = (16,15)
send_index_time = (8,30)

def send_vol():
    send_vol_data()
    print(f"Will send tomorrow's volatility data at {send_vol_time[0]}:{send_vol_time[1]}.")

def send_index():
    update_data()
    extract_data()
    send_data()
    print(f"Will send tomorrow's index data at {send_index_time[0]}:{send_index_time[1]}.")

timez = pytz.timezone('Asia/Shanghai')

scheduler = BlockingScheduler(timezone=timez)
scheduler.add_job(send_index, 'cron', hour=send_index_time[0], minute=send_index_time[1])
scheduler.add_job(send_vol, 'cron', hour=send_vol_time[0], minute=send_vol_time[1])

try:
    print("Start!")
    scheduler.start()
    print(f"Index data sender process initiated. The data will be sent today at {send_index_time[0]}:{send_index_time[1]}.")
    print(f"Volatility data sender process initiated. The data will be sent today at {send_vol_time[0]}:{send_vol_time[1]}.")
except (KeyboardInterrupt, SystemExit):
    pass