import os.path
import base64
import pickle

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path

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
            flow = InstalledAppFlow.from_client_secrets_file('automator/credentials.json', SCOPES)
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
    send_email(
        subject="Daily BTC prices update",
        body="Sup guys! Stuff is attached.",
        to_emails=['ericarcherman@gmail.com', 'tim.ball@signalplus.com', 'nyma.m.sharifi@gmail.com'],
        file_path="extracted_prices.csv"
    )