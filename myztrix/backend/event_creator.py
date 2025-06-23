import os
import sys
import datetime
from googleapiclient.errors import HttpError

# 🔥 Append backend path for local imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from calendar_handler import get_calendar_service

def add_event_to_calendar(summary, description, location, start_datetime, end_datetime):
    """
    Adds an event to the user's primary Google Calendar.
    """
    try:
        service = get_calendar_service()
    except Exception as e:
        print(f"❌ Failed to load calendar service: {e}")
        return None

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'UTC',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 720},
                {'method': 'popup', 'minutes': 120},
                {'method': 'popup', 'minutes': 60},
                {'method': 'popup', 'minutes': 30},
            ],
        },
    }

    try:
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"✅ Event created: {created_event.get('htmlLink')}")
        return created_event.get('id')
    except HttpError as error:
        print(f"⚠️ Failed to create event: {error}")
        return None

