from apscheduler.schedulers.blocking import BlockingScheduler
import pytz

from sender.lark_text import yesterday_data
from sender.lark_text import today_data

send_yesterday_time = (8, 30)
send_today_time = (10, 5)


def send_yesterday_index():
    try:
        yesterday_data()
        print(f"Will send tomorrow's index data at {send_yesterday_time[0]}:{send_yesterday_time[1]}.")
    except Exception as e:
        print(f"send_yesterday_index meet error: {e}")


def send_today_index():
    try:
        today_data()
    except Exception as e:
        print(f"send_today_index meet error: {e}")


timez = pytz.timezone('Asia/Shanghai')

scheduler = BlockingScheduler(timezone=timez)
scheduler.add_job(send_yesterday_index, 'cron', hour=send_yesterday_time[0], minute=send_yesterday_time[1])
scheduler.add_job(send_today_index, 'cron', hour=send_today_time[0], minute=send_today_time[1])
# scheduler.add_job(send_yesterday_index, 'cron', second=30)
# scheduler.add_job(send_today_index, 'cron', second=1)

try:
    print("Start!")
    scheduler.start()
    print(
        f"Index data sender process initiated. The data will be sent today at {send_today_time[0]}:{send_today_time[1]}.")
except (KeyboardInterrupt, SystemExit):
    pass
