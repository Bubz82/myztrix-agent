import sys
import json
from calendar_flask import create_calendar_event

# Test data
event_data = {
    "summary": "Agent War Room Briefing",
    "description": "Prep meeting before operations",
    "location": "HQ Conference Room",
    "start_time": "2025-06-12T10:00:00",
    "end_time": "2025-06-12T11:00:00"
}

print("Testing create_calendar_event function directly")
print("Event data:", json.dumps(event_data, indent=2))

try:
    result = create_calendar_event(event_data)
    print("Success! Event created:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
