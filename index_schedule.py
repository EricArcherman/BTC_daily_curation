from apscheduler.schedulers.blocking import BlockingScheduler
import pytz

from data.update import main as update_data
from extract import main as extract_data
from sender.lark_text import main as send_data

send_index_time = (8,30)

def send_index():
    update_data()
    extract_data()
    send_data()
    print(f"Will send tomorrow's index data at {send_index_time[0]}:{send_index_time[1]}.")

timez = pytz.timezone('Asia/Shanghai')

scheduler = BlockingScheduler(timezone=timez)
scheduler.add_job(send_index, 'cron', hour=send_index_time[0], minute=send_index_time[1])

try:
    print("Start!")
    scheduler.start()
    print(f"Index data sender process initiated. The data will be sent today at {send_index_time[0]}:{send_index_time[1]}.")
except (KeyboardInterrupt, SystemExit):
    pass