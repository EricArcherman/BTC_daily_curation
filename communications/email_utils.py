import os
import base64
import pickle
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
from io import BytesIO

SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

class EmailChain:
    def __init__(self, chain_name, author, members):
        self.chain_name = chain_name
        self.author = author
        self.members = members
        self.service = self.get_service()

    def get_service(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('email_credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return build('gmail', 'v1', credentials=creds)

    def start_chain(self, init_msg):
        message = MIMEMultipart('mixed')
        message['From'] = self.author
        message['To'] = ','.join(self.members)
        message['Subject'] = self.chain_name
        
        # Generate a unique Message-ID
        message_id = f"<{datetime.now().strftime('%Y%m%d%H%M%S')}@gmail.com>"
        message['Message-ID'] = message_id
        
        message.attach(MIMEText(init_msg, 'plain'))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        try:
            self.service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            print(f"Email chain '{self.chain_name}' started.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def clean_snippet(self, snippet):
        main_content = re.split(r'On .*? wrote:', snippet)[0]
        main_content = re.sub(r'&lt;.*?&gt;', '', main_content)
        main_content = re.sub(r'\s+', ' ', main_content).strip()
        return main_content

    def chain_latest(self):
        results = self.service.users().messages().list(userId='me', q=f'subject:{self.chain_name}').execute()
        messages = results.get('messages', [])
        
        if not messages:
            print(f"No emails found for chain '{self.chain_name}'.")
            return None
        
        latest_message_id = messages[0]['id']
        message = self.service.users().messages().get(userId='me', id=latest_message_id).execute()
        snippet = message.get('snippet')
        main_content = self.clean_snippet(snippet)
        
        print(f"Most recent email for chain '{self.chain_name}': {main_content}")
        return main_content
    
    def send_to_chain(self, body, file=None):
        results = self.service.users().messages().list(userId='me', q=f'subject:{self.chain_name}').execute()
        messages = results.get('messages', [])

        if not messages:
            print(f"No emails found for chain '{self.chain_name}'")
            return

        meta_message = messages[0]  # msgs are ordered NEWEST -> OLDEST
        latest_message_id = meta_message['id']
        thread_id = meta_message['threadId']
        message = self.service.users().messages().get(userId='me', id=latest_message_id, format='full').execute()

        # Print out headers and body for debugging
        print("Headers of the latest message:")
        for header in message['payload']['headers']:
            print(f"{header['name']}: {header['value']}")

        message_id = None
        references = []
        for header in message['payload']['headers']:
            if header['name'] == 'Message-ID':
                message_id = header['value']
            elif header['name'] == 'References':
                references = header['value'].split()

        reply = MIMEMultipart()
        reply['From'] = self.author
        reply['To'] = ', '.join(self.members)
        reply['Subject'] = self.chain_name
        if message_id:
            reply['In-Reply-To'] = message_id
            reply['References'] = ' '.join(references)

        time_now = datetime.now().strftime('%Y-%m-%d %H:%M')
        body_text = f"{self.chain_name} {time_now} update:\n\n{body}"
        reply.attach(MIMEText(body_text, 'plain'))

        if file:
            part = MIMEBase('application', 'octet-stream')
            file.seek(0)
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={file.name}')
            reply.attach(part)

        raw_message = base64.urlsafe_b64encode(reply.as_bytes()).decode('utf-8')

        try:
            self.service.users().messages().send(userId='me', body={'raw': raw_message, 'threadId': thread_id}).execute()
            print(f"Replied to chain '{self.chain_name}'")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    chain_name = "Test chain"
    author = 'archermaneric@gmail.com'
    members = ['ericarcherman@gmail.com', 'archermaneric@gmail.com']

    email_chain = EmailChain(chain_name, author, members)

    # (1) Start a new chain
    email_chain.start_chain("Hello, World!")

    # (2) Get the latest message in the chain
    email_chain.chain_latest()

    # (3) Send a reply to the chain
    body = "automated_reply_to_automated_reply"
    file = BytesIO()
    file.write(b'column1,column2\nvalue1,value2')
    file.seek(0)
    file.name = 'test.csv'
    email_chain.send_to_chain(body, file)