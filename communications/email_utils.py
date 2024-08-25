# creating oauth service
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle

# starting email chain
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText

SCOPES = ['https://mail.google.com/']

class EmailChain:
    def __init__(self, chain_name, author, members, creds_file):
        self.chain_name = chain_name
        self.author = author
        self.members = members
        self.creds_file = creds_file

        self.thread_ID = 0 # temporary value

        self.service = self.create_service(creds_file)

    def create_service(self, creds_file):
        creds = None

        # credential logic
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        # building service
        service = build('gmail', 'v1', credentials=creds)
        return service
    
    def init_chain(self, body):
        try:
            # MIMEText object for the email
            message = MIMEText(body)
            message['to'] = ', '.join(self.members)
            message['from'] = self.author
            message['subject'] = self.chain_name

            # message to base64
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            message_body = {'raw': raw}

            # send email
            sent_message = self.service.users().messages().send(userId='me', body=message_body).execute()
            print(f"Thread ID is: {sent_message['threadId']}")
            self.thread_ID = sent_message['threadId']
            return sent_message

        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    @property
    def latest_msg(self):
        try:
            # Get the thread details
            thread = self.service.users().threads().get(userId='me', id=self.thread_ID).execute()
            
            # Extract the list of messages
            messages = thread['messages']
            
            if not messages:
                print("No messages found in this thread.")
                return None
            
            # Sort messages by 'internalDate'
            messages.sort(key=lambda msg: int(msg['internalDate']), reverse=True)
            
            # Get the latest message (the first one in the sorted list)
            latest_message = messages[0]
            
            return latest_message

        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
        
    def msg_to_chain(self, body, attachment):
        pass



















    '''def __init__(self, chain_name, author, members):
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
        message.attach(part)'''

if __name__ == "__main__":
    chain_name = "Test chain"
    author = 'archermaneric@gmail.com'
    members = ['ericarcherman@gmail.com', 'archermaneric@gmail.com']
    creds_file = 'email_credentials.json'

    email_chain = EmailChain(chain_name, author, members, creds_file)

    # (1) Start a new chain
    init_chain_result = email_chain.init_chain("Hello, World!")
    print(email_chain.latest_msg)

    # (2) Get the latest message in the chain
    # email_chain.chain_latest()

    # (3) Send a reply to the chain
    '''from io import BytesIO
    body = "automated_reply_to_automated_reply"
    file = BytesIO()
    file.write(b'column1,column2\nvalue1,value2')
    file.seek(0)
    file.name = 'test.csv'
    email_chain.send_to_chain(body, file)'''