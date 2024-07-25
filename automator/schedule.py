from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

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

scheduler = BlockingScheduler()
scheduler.add_job(main, 'cron', hour=10, minute=40)

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass