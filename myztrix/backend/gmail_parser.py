# gmail_parser.py
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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Project base dir to resolve paths reliably no matter where script is run
BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar'
]

TOKEN_PATH = BASE_DIR / 'credentials' / 'token.json'
CREDS_PATH = BASE_DIR / 'Config' / 'credentials.json'

MEETING_KEYWORDS = {
    'meeting', 'call', 'appointment', 'schedule', 'calendar',
    'invite', 'invitation', 'conference', 'discussion'
}

class GmailAgent:
    def __init__(self, credentials_path: pathlib.Path = CREDS_PATH, token_path: pathlib.Path = TOKEN_PATH):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.credentials = None
        self.service = None

        # NLTK setup
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
            if self.token_path.exists():
                try:
                    with open(self.token_path, 'r') as token_file:
                        self.credentials = Credentials.from_authorized_user_info(json.load(token_file), SCOPES)
                except Exception as e:
                    logger.warning(f"Corrupted token.json. Re-authenticating. Cause: {str(e)}")
                    self.credentials = None

            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), SCOPES)
                    self.credentials = flow.run_local_server(port=0)

                # Save new token
                with open(self.token_path, 'w') as token_file:
                    token_file.write(self.credentials.to_json())

            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Authentication successful.")
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False

    # (Keep your other methods unchanged except use pathlib.Path for token paths if any)

def add_event_to_calendar(event: Dict) -> bool:
    try:
        creds = None

        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), ["https://www.googleapis.com/auth/calendar"])

        if creds and creds.expired and creds.refresh_token:
            logger.info("[INFO] Refreshing expired token...")
            creds.refresh(Request())
            with open(TOKEN_PATH, "w") as token_file:
                token_file.write(creds.to_json())

        service = build("calendar", "v3", credentials=creds)

        start_time = event.get("start_time") or datetime.now().isoformat()
        end_time = event.get("end_time") or (datetime.now() + timedelta(hours=1)).isoformat()

        calendar_event = {
            "summary": event.get("title", "New Event"),
            "location": event.get("location", ""),
            "description": event.get("description", ""),
            "start": {
                "dateTime": start_time,
                "timeZone": "Africa/Johannesburg",  # Adjust to your actual timezone or make configurable
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "Africa/Johannesburg",
            },
        }

        created_event = service.events().insert(calendarId="primary", body=calendar_event).execute()
        logger.info(f"Event created: {created_event.get('htmlLink')}")
        return True

    except Exception as e:
        logger.error(f"[!] Failed to add event: {e}")
        return False
