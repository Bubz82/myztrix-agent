import time
import platform
from threading import Thread

if platform.system() == "Darwin":
    from pync import Notifier

    def notify(title, message):
        Notifier.notify(message, title=title)

else:
    # On non-mac, mock notify with print
    def notify(title, message):
        print(f"🔔 [MOCK] {title} - {message}")

def schedule_notifications(event):
    """
    event: dict with keys like 'start_time' (ISO string), 'summary', 'description'
    """

    from datetime import datetime, timedelta
    import dateutil.parser

    start = dateutil.parser.isoparse(event['start_time'])

    times = {
        "Morning of event": datetime.combine(start.date(), datetime.min.time()),
        "2 hours before": start - timedelta(hours=2),
        "1 hour before": start - timedelta(hours=1),
        "30 minutes before": start - timedelta(minutes=30),
    }

    def run_schedule():
        now = datetime.now()
        for label, notify_time in sorted(times.items(), key=lambda x: x[1]):
            delay = (notify_time - now).total_seconds()
            if delay > 0:
                time.sleep(delay)
                notify(f"Upcoming Event: {event['summary']}", f"{label} - {event.get('description', '')}")

    Thread(target=run_schedule, daemon=True).start()