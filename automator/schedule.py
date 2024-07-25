from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess
import pytz

def update_data():
    subprocess.run(['/usr/local/bin/python3', 'data/update.py'])

def extract_data():
    subprocess.run(['/usr/local/bin/python3', 'extract.py'])

def send_data():
    subprocess.run(['/usr/local/bin/python3', "sender/lark_text.py"])

def main():
    update_data()
    extract_data()
    send_data()

timez = pytz.timezone('Asia/Shanghai')

scheduler = BlockingScheduler(timezone=timez)
scheduler.add_job(main, 'cron', second=9)

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass