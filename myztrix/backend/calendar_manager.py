import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Define scope explicitly
SCOPES = ['https://www.googleapis.com/auth/calendar']

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CalendarManager:
    def __init__(self, credentials_path: str, token_path: str):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.credentials = None

    def authenticate(self) -> bool:
        """Authenticate with Google Calendar API using OAuth2."""
        try:
            token_file = Path(self.token_path)

            if token_file.exists():
                self.credentials = Credentials.from_authorized_user_file(self.token_path, SCOPES)

            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    raise Exception("No valid credentials found. Authenticate with Gmail first.")

                with open(self.token_path, 'w') as token:
                    token.write(self.credentials.to_json())

            self.service = build('calendar', 'v3', credentials=self.credentials)
            return True

        except Exception as e:
            logger.error(f"Calendar authentication failed: {str(e)}")
            return False

    def create_event(self, event_details: Dict) -> Optional[str]:
        """
        Create a calendar event with layered reminders.
        Returns the event ID if successful, None otherwise.
        """
        try:
            if not self.service:
                if not self.authenticate():
                    return None

            # Parse times safely
            start_time = datetime.fromisoformat(event_details.get('start_time', datetime.utcnow().isoformat()))
            end_time = datetime.fromisoformat(
                event_details.get('end_time', (start_time + timedelta(hours=1)).isoformat())
            )

            event = {
                'summary': event_details.get('title', 'New Event'),
                'description': event_details.get('description', ''),
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 120},
                        {'method': 'popup', 'minutes': 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }

            if 'attendees' in event_details:
                event['attendees'] = [{'email': email.strip()} for email in event_details['attendees']]

            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'
            ).execute()

            logger.info(f"✅ Created calendar event: {created_event['id']}")
            return created_event['id']

        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            return None

    def process_pending_events(self, pending_events_path: str) -> None:
        """Process all pending events and create them in the calendar."""
        try:
            if not os.path.exists(pending_events_path):
