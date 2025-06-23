import os
import sys
import json

# Add backend folder to sys.path BEFORE any imports that rely on it
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, request, render_template
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import pytz
from datetime import datetime, timedelta
import dateutil.parser
import tzlocal  # grab local timezone

# Use **relative imports** or absolute but *correct sys.path* so Python can find local modules

from gmail_scraper import (
    get_gmail_service,
    list_unread_messages,
    get_message,
    extract_email_text,
    mark_as_read,
    parse_event_details
)

from calendar_handler import (
    get_calendar_service,
    add_event,
    create_event_payload
)

from event_creator import add_event_to_calendar
from notifications import schedule_notifications

DECLINED_FILE = os.path.join(BASE_DIR, 'declined_events.json')
PENDING_FILE = os.path.join(BASE_DIR, 'pending_events.json')
EVENTS_FILE = os.path.join(BASE_DIR, 'events.json')

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, 'r') as f:
        content = f.read().strip()
        if not content:
            return []
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return []

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)


@app.route('/')
def home():
    pending_events = load_json(PENDING_FILE)
    return render_template('index.html', events=pending_events)

@app.route('/scan', methods=['GET'])
def scan_events():
    try:
        events = load_json(EVENTS_FILE)
        return jsonify({'status': 'success', 'events': events}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/check_emails', methods=['GET'])
def check_emails():
    try:
        calendar_service = get_calendar_service()
        creds = calendar_service._credentials
        gmail_service = get_gmail_service(creds)
        messages = list_unread_messages(gmail_service)
    except Exception as e:
        return jsonify({"error": f"Failed to connect to Google APIs: {e}"}), 500

    flagged_events = []
    pending = load_json(PENDING_FILE)

    for msg in messages:
        try:
            msg_data = get_message(gmail_service, msg['id'])
            text = extract_email_text(msg_data['payload'])
            event_lines = [
                line for line in text.splitlines()
                if any(k in line.lower() for k in ['meeting', 'call', 'talk', 'presentation', 'event', 'trip', 'flight', 'reservation'])
            ]

            for line in event_lines:
                parsed_event = parse_event_details(line)
                if not parsed_event:
                    continue

                subject = parsed_event['summary']
                description = parsed_event['description']
                start_time = parsed_event['start_time']

                event_payload = create_event_payload(subject, description, start_time)
                added_event = add_event(calendar_service, event_data=event_payload)
                mark_as_read(gmail_service, msg['id'])

                flagged_event = {
                    "summary": subject,
                    "description": description,
                    "start_time": start_time.isoformat(),
                    "calendar_event_id": added_event.get('id', 'unknown')
                }

                flagged_events.append(flagged_event)
                pending.append(flagged_event)

                break  # One event per message

        except Exception as e:
            print(f"Skipping message {msg['id']} due to error: {e}")
            continue

    if flagged_events:
        save_json(PENDING_FILE, pending)
        return jsonify({"flagged_events": flagged_events}), 200
    else:
        return jsonify({"message": "No event triggers found in unread emails"}), 200

@app.route('/confirm', methods=['POST'])
def confirm_event():
    event = request.json
    try:
        summary = event.get('summary', 'No title')
        description = event.get('description', '')
        location = event.get('location', '')
        start_time = event.get('start_time')
        end_time = event.get('end_time')

        if not (start_time and end_time):
            raise ValueError("Missing start or end time")

        start_datetime = datetime.fromisoformat(start_time)
        end_datetime = datetime.fromisoformat(end_time)

        # Force timezone awareness
        local_tz = tzlocal.get_localzone()
        start_datetime = start_datetime.replace(tzinfo=local_tz)
        end_datetime = end_datetime.replace(tzinfo=local_tz)

        add_event_to_calendar(summary, description, location, start_datetime, end_datetime)
        return jsonify({'status': 'success', 'message': 'Event confirmed and added to calendar.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Failed to confirm event: {str(e)}'})

@app.route('/decline', methods=['POST'])
def decline_event():
    if not request.is_json:
        return jsonify({'status': 'error', 'message': 'Invalid or missing JSON'}), 400

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'status': 'error', 'message': 'No event data provided'}), 400

    declined = load_json(DECLINED_FILE)
    declined.append(data)
    save_json(DECLINED_FILE, declined)
    return jsonify({'status': 'success'}), 200

@app.route('/declined')
def show_declined():
    events = load_json(DECLINED_FILE)
    return render_template('declined.html', events=events)

@app.route('/recover', methods=['POST'])
def recover_event():
    event = request.json
    if not event:
        return jsonify({'status': 'error', 'message': 'No event data'}), 400
    declined = load_json(DECLINED_FILE)
    declined = [e for e in declined if e != event]
    save_json(DECLINED_FILE, declined)
    pending = load_json(PENDING_FILE)
    pending.append(event)
    save_json(PENDING_FILE, pending)
    return jsonify({'status': 'success', 'message': 'Event recovered.'}), 200

@app.route('/delete_declined', methods=['POST'])
def delete_declined():
    event = request.json
    if not event:
        return jsonify({'status': 'error', 'message': 'No event data'}), 400
    declined = load_json(DECLINED_FILE)
    declined = [e for e in declined if e != event]
    save_json(DECLINED_FILE, declined)
    return jsonify({'status': 'success', 'message': 'Declined event deleted.'}), 200

def schedule_notifications(event):
    try:
        start = dateutil.parser.isoparse(event['start_time']).astimezone(pytz.UTC)
        now = datetime.now(pytz.UTC)
        notify_times = [
            start.replace(hour=8, minute=0, second=0, microsecond=0),
            start - timedelta(hours=2),
            start - timedelta(hours=1),
            start - timedelta(minutes=30)
        ]
        for notify_time in notify_times:
            if notify_time > now:
                print(f"Notification scheduled for: {notify_time} → {event.get('summary', 'No Title')}")
    except Exception as e:
        print(f"Failed to schedule notifications: {e}")

if __name__ == '__main__':
    app.run(port=5000, debug=True)





