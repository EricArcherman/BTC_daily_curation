from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

def update_data():
    subprocess.run(['/usr/local/bin/python3', "data/update.py"])

def send_data():
    subprocess.run(['/usr/local/bin/python3', "email/sender.py"])

def main():
    update_data()
    send_data()

scheduler = BlockingScheduler()
scheduler.add_job(main, 'cron', hour=8, minute=20)

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass