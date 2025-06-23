# calendar_flask.py
import datetime
from google.oauth2.credentials import Credentials
import os
from backend.event_creator import add_event_to_calendar

def create_calendar_event(event_data):
    """
    Create a calendar event from the provided event data.
    
    Args:
        event_data (dict): A dictionary containing event details:
            - summary: Event title
            - description: Event description
            - location: Event location
            - start_time: ISO format datetime string for event start
            - end_time: ISO format datetime string for event end (optional)
            
    Returns:
        dict: The created event details
    """
    # Extract event details
    summary = event_data.get('summary', 'Untitled Event')
    description = event_data.get('description', '')
    location = event_data.get('location', '')
    
    # Parse start time
    start_time = event_data.get('start_time')
    if not start_time:
        raise ValueError("Missing required field: start_time")
    
    start_datetime = datetime.datetime.fromisoformat(start_time)
    
    # Add event to calendar
    event_id = add_event_to_calendar(summary, description, location, start_datetime)
    
    if not event_id:
        raise Exception("Failed to create calendar event")
    
    # Return success response with event details
    return {
        'id': event_id,
        'summary': summary,
        'description': description,
        'location': location,
        'start_time': start_time,
        'created': True
    }
