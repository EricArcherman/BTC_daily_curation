import smtplib
import schedule
import time
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load configuration from file
with open('automator/config.json') as config_file:
    config = json.load(config_file)

smtp_server = config['smtp_server']
smtp_port = config['smtp_port']
email_address = config['email_address']
email_password = config['email_password']
to_email = config['to_email']
subject = 'Good Morning!'
body = 'Good morning!'

def send_email():
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_address, email_password)
        text = msg.as_string()
        server.sendmail(email_address, to_email, text)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Schedule the task
schedule.every().day.at("20:00").do(send_email)

print("Scheduling email task...")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute if it's time to run the task