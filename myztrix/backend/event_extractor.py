# event_extractor.py
import re
from datetime import datetime, timedelta
import dateutil.parser

EVENT_KEYWORDS = ["meeting", "call", "appointment", "talk", "trip", "event", "conference", "flight", "webinar", "presentation"]

def extract_event_candidates(emails):
    events = []

    for email in emails:
        subject = email['subject'].lower()
        body = email['body'].lower()
        text = subject + ' ' + body

        if any(keyword in text for keyword in EVENT_KEYWORDS):
            possible_times = extract_times(text)
            for time in possible_times:
                events.append({
                    'subject': email['subject'],
                    'sender': email['sender'],
                    'snippet': email['body'][:200],
                    'timestamp': time,
                    'source': email['id']
                })

    return events

def extract_times(text):
    time_matches = []
    try:
        potential_dates = re.findall(r'\b(?:on )?(?:next )?\w+\s\d{1,2}(?:st|nd|rd|th)?(?:,?\s\d{4})?', text)
        potential_times = re.findall(r'\b\d{1,2}(:\d{2})?\s?(am|pm)?\b', text)

        now = datetime.now()
        for date_str in potential_dates:
            try:
                parsed_date = dateutil.parser.parse(date_str, fuzzy=True, default=now)
                time_matches.append(parsed_date)
            except:
                continue

        if not time_matches:
            guess = dateutil.parser.parse(text, fuzzy=True, default=now)
            time_matches.append(guess)
    except:
        pass

    return time_matches