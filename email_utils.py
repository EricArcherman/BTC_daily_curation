import os

import base64
import pickle

import pandas as pd
from datetime import datetime

# Mulipurpose Internet Mail Extension (MIME) email library
from email.mime.multipart import MIMEMultipart # base class for multipart emails (text, attachments, etc.)
from email.mime.text import MIMEText # text
from email.mime.base import MIMEBase # attachments
from email import encoders # convert data into format suitable for SMTP email protocol

# google Open Authorization (OAuth) library
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path # for working with files

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.picle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('email_credentials.json', SCOPES)
            