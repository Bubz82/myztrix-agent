import datetime
import pytz
from scheduler import schedule_event_notifications, scheduler

def dummy_notify(event):
    print(f"Notify called for {event['summary']}")

def test_schedule_event_notifications(monkeypatch):
    calls = []

    def fake_notify(event):
        calls.append(event['id'])

    # Patch send_notification in scheduler.py
    monkeypatch.setattr('scheduler.send_notification', fake_notify)

    event = {
        'id': 'test123',
        'summary': 'Test Meeting',
        'start_time': datetime.datetime.now(pytz.UTC) + datetime.timedelta(hours=3)
    }

    schedule_event_notifications(event)

    jobs = scheduler.get_jobs()
    assert any(job.id.startswith('notify_test123') for job in jobs)

    # Cleanup after test
    for job in jobs:
        if job.id.startswith('notify_test123'):
            scheduler.remove_job(job.id)