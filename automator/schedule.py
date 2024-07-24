from apscheduler.schedulers.blocking import BlockingScheduler
import subprocess

def update_data():
    subprocess.run(['/usr/local/bin/python3', "data/update.py"])

def reformat_data():
    subprocess.run(['/usr/local/bin/python3', 'extract.py'])

def send_data():
    subprocess.run(['/usr/local/bin/python3', "email/sender.py"])

def main():
    update_data()
    reformat_data()
    send_data()

scheduler = BlockingScheduler()
scheduler.add_job(main, 'cron', hour=12, minute=00)

try:
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    pass