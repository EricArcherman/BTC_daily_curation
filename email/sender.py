import os

import base64
import pickle

import pandas as pd
from datetime import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path

RUNNING = 'data/running-2-years.csv'

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('email/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def send_email(subject, body, to_emails, file_path):
    from_email = 'archermaneric@gmail.com'

    creds = get_credentials()
    service = build('gmail', 'v1', credentials=creds)

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with open(file_path, 'rb') as file:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(file.read())
    encoders.encode_base64(attachment)
    attachment.add_header(
        'Content-Disposition',
        f'attachment; filename={Path(file_path).name}',
    )
    msg.attach(attachment)

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    try:
        message = service.users().messages().send(userId="me", body={'raw': raw}).execute()
        print(f"Message Id: {message['id']}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    with open(RUNNING, 'rb') as f:
        f.seek(-2, 2)
        while f.read(1) != b'\n':
            f.seek(-2, 1)
        last_line = f.readline().decode()
    
    timestamp_str = last_line.split(",")[0]
    timestamp = int(timestamp_str)

    last_update = datetime.fromtimestamp(timestamp / 1000)
    last_update_readable = last_update.strftime('%Y-%m-%d %H:%M:%S')

    send_email(
        subject="Daily BTC update",
        body=f"Sup guys! The curated prices are below, last data update was at {last_update_readable}",
        to_emails=['ericarcherman@gmail.com'],# , 'tim.ball@signalplus.com', 'nyma.m.sharifi@gmail.com'],
        file_path="extracted_prices.csv"
    )