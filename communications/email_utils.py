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

SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

class EmailChain:
    def __init__(self, chain_name, author, members):
        self.chain_name = chain_name
        self.author = author
        self.members = members
        self.service = self.get_service()

    def get_service(self):
        """Retrieve the Gmail API service using stored credentials or by performing OAuth."""
        creds = self.load_credentials()
        if not creds or not creds.valid:
            creds = self.refresh_or_authorize(creds)
            self.save_credentials(creds)
        return build('gmail', 'v1', credentials=creds)

    def load_credentials(self):
        """Load credentials from token.pickle if it exists."""
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                return pickle.load(token)
        return None

    def refresh_or_authorize(self, creds):
        """Refresh expired credentials or perform OAuth if no valid credentials exist."""
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('email_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        return creds

    def save_credentials(self, creds):
        """Save credentials to token.pickle."""
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    def start_chain(self, init_msg):
        """Start a new email chain with an initial message."""
        raw_message = self.create_message(self.chain_name, init_msg)
        self.send_raw_message(raw_message)
        print(f"Email chain '{self.chain_name}' started.")

    def create_message(self, subject, body, in_reply_to=None, references=None):
        """Create a MIME message with the given subject, body, and optional reply headers."""
        message = MIMEMultipart()
        message['From'] = self.author
        message['To'] = ','.join(self.members)
        message['Subject'] = subject
        if in_reply_to:
            message['In-Reply-To'] = in_reply_to
            message['References'] = ' '.join(references)
        message.attach(MIMEText(body, 'plain'))
        return base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    def send_raw_message(self, raw_message, thread_id=None):
        """Send the raw MIME message using the Gmail API."""
        try:
            self.service.users().messages().send(userId='me', body={'raw': raw_message, 'threadId': thread_id}).execute()
        except Exception as e:
            print(f"An error occurred: {e}")

    def clean_snippet(self, snippet):
        """Clean the email snippet to extract the main content."""
        main_content = re.split(r'On .*? wrote:', snippet)[0]
        main_content = re.sub(r'&lt;.*?&gt;', '', main_content)
        return re.sub(r'\s+', ' ', main_content).strip()

    def chain_latest(self):
        """Fetch the latest email in the chain."""
        message = self.get_latest_message()
        if not message:
            print(f"No emails found for chain '{self.chain_name}'.")
            return None
        snippet = message.get('snippet')
        main_content = self.clean_snippet(snippet)
        print(f"Most recent email for chain '{self.chain_name}': {main_content}")
        return main_content

    def get_latest_message(self):
        """Retrieve the latest message in the chain."""
        results = self.service.users().messages().list(userId='me', q=f'subject:{self.chain_name}').execute()
        messages = results.get('messages', [])
        if not messages:
            return None
        latest_message_id = messages[0]['id']
        return self.service.users().messages().get(userId='me', id=latest_message_id).execute()

    def send_to_chain(self, body, file=None):
        """Send a reply to the latest email in the chain."""
        message = self.get_latest_message()
        if not message:
            print(f"No emails found for chain '{self.chain_name}'")
            return
        
        references, in_reply_to = self.extract_reply_headers(message)
        reply_body = self.create_reply_body(body)
        raw_message = self.create_message(self.chain_name, reply_body, in_reply_to, references)

        if file:
            self.attach_file(raw_message, file)

        self.send_raw_message(raw_message, thread_id=message['threadId'])
        print(f"Replied to chain '{self.chain_name}'")

    def extract_reply_headers(self, message):
        """Extract the 'References' and 'In-Reply-To' headers from the message."""
        references, in_reply_to = [], None
        for header in message['payload']['headers']:
            if header['name'] == 'References':
                references = header['value'].split()
            elif header['name'] == 'Message-ID':
                in_reply_to = header['value']
        if in_reply_to:
            references.append(in_reply_to)
        return references, in_reply_to

    def create_reply_body(self, body):
        """Create the body for the reply message, including a timestamp."""
        time_now = datetime.now().strftime('%Y-%m-%d %H:%M')
        return f"{self.chain_name} {time_now} update:\n{body}"

    def attach_file(self, message, file):
        """Attach a file to the MIME message."""
        part = MIMEBase('application', 'octet-stream')
        file.seek(0)
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={file.name}')
        message.attach(part)

if __name__ == "__main__":
    chain_name = "Test chain"
    author = 'archermaneric@gmail.com'
    members = ['ericarcherman@gmail.com', 'archermaneric@gmail.com']

    email_chain = EmailChain(chain_name, author, members)

    # (1) Start a new chain
    email_chain.start_chain("Hello, World!")

    # (2) Get the latest message in the chain
    # email_chain.chain_latest()

    # (3) Send a reply to the chain
    from io import BytesIO
    body = "automated_reply_to_automated_reply"
    file = BytesIO()
    file.write(b'column1,column2\nvalue1,value2')
    file.seek(0)
    file.name = 'test.csv'
    email_chain.send_to_chain(body, file)