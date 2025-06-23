# calendar_inserter.py

from __future__ import print_function
import datetime
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import os.path
from auth import get_calendar_service
from backend.calendar_inserter import insert_event_to_calendar

insert_event_to_calendar(event_data)

def create_event(summary, location, description, start_time, end_time, timezone='auto'):
    service = get_calendar_service()
    
    if timezone == 'auto':
        # Use system timezone
        tz = datetime.datetime.now().astimezone().tzinfo.zone
    else:
        tz = timezone  # fallback or override

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': tz,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': tz,
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 60 * 24},   # Morning of (assume 24h before)
                {'method': 'popup', 'minutes': 120},       # 2 hours
                {'method': 'popup', 'minutes': 60},        # 1 hour
                {'method': 'popup', 'minutes': 30},        # 30 minutes
            ],
        },
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"🎯 Event created: {created_event.get('htmlLink')}")
    return created_event.get('id')

def confirm_and_add_event(event_data):
    """
    Confirmed UI will call this with parsed event data.
    event_data = {
        'summary': str,
        'location': str,
        'description': str,
        'start_time': datetime obj,
        'end_time': datetime obj
    }
    """
    event_id = create_event(
        summary=event_data['summary'],
        location=event_data['location'],
        description=event_data['description'],
        start_time=event_data['start_time'],
        end_time=event_data['end_time']
    )
    return event_id
