import base64
import datetime
from googleapiclient.discovery import build
from email import message_from_bytes
from bs4 import BeautifulSoup
import dateparser
import os

TRIGGER_KEYWORDS = ['meeting', 'call', 'talk', 'presentation', 'event', 'trip', 'flight', 'reservation']

def get_gmail_service(creds=None):
    """
    Return the Gmail API service object.
    If creds provided, use them; else load from token.json.
    """
    from google.oauth2.credentials import Credentials

    if creds:
        return build('gmail', 'v1', credentials=creds)

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file(
            'token.json',
            ['https://www.googleapis.com/auth/gmail.readonly']
        )
        return build('gmail', 'v1', credentials=creds)
    else:
        raise Exception("token.json not found. Run OAuth flow first.")

def extract_email_text(message_payload):
    """Extract plain text or fallback from HTML from Gmail message payload."""
    if not message_payload:
        return ''
    parts = message_payload.get('parts', [])
    if not parts:
        # Sometimes message body is directly in 'body'
        if 'body' in message_payload and 'data' in message_payload['body']:
            data = message_payload['body']['data']
            text = base64.urlsafe_b64decode(data).decode('utf-8')
            return text
        return ''

    for part in parts:
        mime = part.get('mimeType', '')
        data = part.get('body', {}).get('data', None)
        if not data:
            continue
        decoded_bytes = base64.urlsafe_b64decode(data)
        if mime == 'text/plain':
            return decoded_bytes.decode('utf-8', errors='ignore')
        elif mime == 'text/html':
            html = decoded_bytes.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
    return ''

def extract_event_candidates(text):
    """Return list of lines containing any trigger keyword (case-insensitive)."""
    if not text:
        return []
    lines = text.splitlines()
    event_lines = []
    for line in lines:
        if any(keyword in line.lower() for keyword in TRIGGER_KEYWORDS):
            event_lines.append(line.strip())
    return event_lines

def parse_event_details(event_line):
    """Parse date/time from line; return event dict or None."""
    parsed_date = dateparser.parse(event_line, settings={'PREFER_DATES_FROM': 'future'})
    if not parsed_date:
        return None

    summary = (event_line[:80] + '...') if len(event_line) > 80 else event_line
    return {
        'summary': summary,
        'description': event_line,
        'location': '',
        'start_time': parsed_date,
        'end_time': parsed_date + datetime.timedelta(hours=1),
    }

def list_unread_messages(service, max_results=10):
    """
    Return a list of unread Gmail messages from the inbox.
    """
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX', 'UNREAD'],
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    return messages

def get_message(service, msg_id, format='full'):
    """
    Fetch a Gmail message by ID.
    """
    message = service.users().messages().get(
        userId='me',
        id=msg_id,
        format=format
    ).execute()
    return message

def scan_recent_messages(creds, max_results=10):
    service = get_gmail_service(creds)
    """
    Scan inbox, extract and parse event candidates from unread emails.
    """
    messages = list_unread_messages(service, max_results=max_results)

    candidates = []

    for msg in messages:
        msg_data = get_message(service, msg['id'], format='full')
        payload = msg_data.get('payload', {})
        text = extract_email_text(payload)
        if not text:
            continue

        lines = extract_event_candidates(text)
        for line in lines:
            parsed = parse_event_details(line)
            if parsed:
                candidates.append(parsed)

    return candidates

def find_event_triggers(text):
    """
    Return a list of trigger dicts with text and parsed dates.
    Fits expected interface from main.py.
    """
    triggers = []
    lines = extract_event_candidates(text)
    for line in lines:
        parsed_date = dateparser.parse(line, settings={'PREFER_DATES_FROM': 'future'})
        triggers.append({
            'text': line,
            'dates': [parsed_date] if parsed_date else []
        })
    return triggers

def mark_as_read(service, msg_id):
    """
    Mark a Gmail message as read by removing the UNREAD label.
    """
    service.users().messages().modify(
        userId='me',
        id=msg_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()

