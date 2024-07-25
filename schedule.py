from apscheduler.schedulers.blocking import BlockingScheduler
import pytz

from data.update import main as update_data
from extract import main as extract_data
from sender.lark_text import main as send_data

def main():
    update_data()
    extract_data()
    send_data()

timez = pytz.timezone('Asia/Shanghai')

scheduler = BlockingScheduler(timezone=timez)
scheduler.add_job(main, 'cron', second=9)

try:
    print("Start!")
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass