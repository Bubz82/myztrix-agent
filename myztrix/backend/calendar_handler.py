import os
import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_app_support_dir():
    """
    Determines where to look for token.json depending on OS.
    """
    if os.name == 'posix':
        # macOS standard location
        return os.path.expanduser('~/Library/Application Support/MyztrixAgent')
    else:
        # Windows fallback for development/testing
        return os.path.join(os.getcwd(), 'backend', 'dev_config')

APP_SUPPORT_DIR = get_app_support_dir()
TOKEN_PATH = os.path.join(APP_SUPPORT_DIR, 'token.json')

def get_calendar_service(creds=None):
    """
    Return a Google Calendar API service object.
    If creds not provided, tries loading from secure TOKEN_PATH.
    """
    if creds:
        return build('calendar', 'v3', credentials=creds)

    if not os.path.exists(TOKEN_PATH):
        raise Exception(f"token.json not found in {TOKEN_PATH}. Run OAuth flow first.")

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    return build('calendar', 'v3', credentials=creds)

def create_event_payload(summary, description, event_date, location=''):
    """
    Build the event JSON payload to send to Google Calendar API.
    """
    if event_date.tzinfo is None:
        event_date = event_date.replace(tzinfo=datetime.timezone.utc)

    start_time = event_date.isoformat()
    end_time = (event_date + datetime.timedelta(hours=1)).isoformat()

    return {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'UTC',
        },
        'reminders': {
            'useDefault': True,
        },
    }

def add_event(service, event_data):
    """
    Add an event to the primary calendar.
    """
    created_event = service.events().insert(
        calendarId='primary',
        body=event_data
    ).execute()
    return created_event



