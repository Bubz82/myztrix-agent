import os
import json
import logging
import base64
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pathlib

import dateparser
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar'
]

BASE_DIR = pathlib.Path(__file__).parent.resolve()  # Adjust if needed
TOKEN_PATH = str(BASE_DIR / "credentials" / "token.json")
CREDS_PATH = str(BASE_DIR / "credentials" / "credentials.json")

MEETING_KEYWORDS = {
    'meeting', 'call', 'appointment', 'schedule', 'calendar',
    'invite', 'invitation', 'conference', 'discussion'
}

class GmailAgent:
    def __init__(self, credentials_path: str = CREDS_PATH, token_path: str = TOKEN_PATH):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.credentials = None
        self.service = None

        # NLTK setup — ensure required data is available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')

        self.stopwords = set(stopwords.words('english'))

    def authenticate(self) -> bool:
        try:
            if os.path.exists(self.token_path):
                try:
                    # This works better for token.json created by to_json()
                    self.credentials = Credentials.from_authorized_user_file(self.token_path, SCOPES)
                except Exception as e:
                    logger.warning(f"Corrupted token.json. Re-authenticating. Cause: {str(e)}")
                    self.credentials = None

            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                    self.credentials = flow.run_local_server(port=0)

                with open(self.token_path, 'w') as token:
                    token.write(self.credentials.to_json())

            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Authentication successful.")
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False

    def get_unread_emails(self) -> List[Dict]:
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['UNREAD'],
                q='in:inbox'
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

                body = ''
                # Defensive checks for multipart or single-part emails
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part.get('mimeType') == 'text/plain':
                            body_data = part.get('body', {}).get('data')
                            if body_data:
                                body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                            break
                else:
                    body_data = msg['payload'].get('body', {}).get('data')
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')

                emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body': body
                })

            return emails

        except Exception as e:
            logger.error(f"Error fetching unread emails: {str(e)}")
            return []

    def detect_event(self, email: Dict) -> Tuple[bool, float, Optional[Dict]]:
        try:
            text = f"{email['subject']} {email['body']}"
            tokens = word_tokenize(text.lower())
            tokens = [t for t in tokens if t not in self.stopwords]

            keyword_matches = sum(1 for t in tokens if t in MEETING_KEYWORDS)
            keyword_score = min(keyword_matches / 3, 1.0)

            parsed_date = dateparser.parse(text, fuzzy=True)
            date_score = 1.0 if parsed_date else 0.0

            confidence = (keyword_score * 0.6) + (date_score * 0.4)

            if confidence >= 0.6 and parsed_date:
                event_details = {
                    'title': email['subject'],
                    'start_time': parsed_date.isoformat(),
                    'end_time': (parsed_date + timedelta(hours=1)).isoformat(),
                    'description': email['body'],
                    'email_id': email['id']
                }
                return True, confidence, event_details

            return False, confidence, None

        except Exception as e:
            logger.error(f"Error detecting event: {str(e)}")
            return False, 0.0, None

    def mark_as_read(self, email_id: str) -> bool:
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {str(e)}")
            return False

    def add_label(self, email_id: str, label_name: str) -> bool:
        try:
            labels_response = self.service.users().labels().list(userId='me').execute()
            labels = labels_response.get('labels', [])
            label_id = None

            for label in labels:
                if label.get('name') == label_name:
                    label_id = label.get('id')
                    break

            if not label_id:
                created_label = self.service.users().labels().create(
                    userId='me',
                    body={'name': label_name}
                ).execute()
                label_id = created_label.get('id')

            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            return True

        except Exception as e:
            logger.error(f"Error adding label: {str(e)}")
            return False


def add_event_to_calendar(event: Dict) -> bool:
    try:
        if not os.path.exists(TOKEN_PATH):
            logger.error("Token file not found for calendar access.")
            return False

        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if creds and creds.expired and creds.refresh_token:
            logger.info("[INFO] Refreshing expired token...")
            creds.refresh(Request())
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        service = build("calendar", "v3", credentials=creds)

        start_time = event.get("start_time") or datetime.utcnow().isoformat() + 'Z'
        end_time = event.get("end_time") or (datetime.utcnow() + timedelta(hours=1)).isoformat() + 'Z'

        calendar_event = {
            "summary": event.get("title", "New Event"),
            "location": event.get("location", ""),
            "description": event.get("description", ""),
            "start": {
                "dateTime": start_time,
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "UTC",
            },
        }

        service.events().insert(calendarId="primary", body=calendar_event).execute()
        logger.info(f"✅ Event added to calendar: {calendar_event['summary']}")
        return True

    except Exception as e:
        logger.error(f"Failed to add event to calendar: {e}")
        return False
