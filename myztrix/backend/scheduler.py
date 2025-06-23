from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import datetime
import pytz
import subprocess

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}

scheduler = BackgroundScheduler(jobstores=jobstores, timezone=pytz.UTC)
scheduler.start()

def schedule_notification(event_id, notify_time, notify_func, *args, **kwargs):
    """
    Schedule a notification job.
    event_id: unique event identifier, used as job id to avoid duplicates
    notify_time: datetime object in UTC
    notify_func: callable function to execute at notify_time
    args, kwargs: passed to notify_func
    """
def is_gmail_active():
    result = subprocess.run(["osascript", "-e",
        'tell application "System Events" to (name of processes) contains "Mail"'],
        capture_output=True, text=True)
    return "true" in result.stdout.lower()
    job_id = f"notify_{event_id}_{int(notify_time.timestamp())}"
if is_gmail_active():
    from backend.gmail_agent import scrape_and_process_gmail
    scrape_and_process_gmail()

    # Remove existing job if duplicate
    existing_job = scheduler.get_job(job_id)
    if existing_job:
        scheduler.remove_job(job_id)

    scheduler.add_job(
        notify_func,
        'date',
        run_date=notify_time,
        args=args,
        kwargs=kwargs,
        id=job_id,
        replace_existing=True
    )

def shutdown_scheduler():
    scheduler.shutdown()