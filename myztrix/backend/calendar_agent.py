import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import getpass
from pathlib import Path
import subprocess
import tzlocal

# === PATHS and CONFIG ===
BASE_DIR = Path.home() / "myztrix" / "backend"
TOKEN_PATH = BASE_DIR / "credentials" / "token.json"
PENDING_EVENTS_PATH = BASE_DIR / "data" / "pending_events.json"
STATUS_PATH = BASE_DIR / "data" / "status.json"
LOG_PATH = BASE_DIR / "logs" / "errors.log"

MAC_USERNAME = getpass.getuser()

# === SETUP LOGGING ===
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === FLASK APP ===
app = Flask(__name__)

# === NOTIFICATION FALLBACK ===
try:
    from macos_notifications import notify_user
except ImportError:
    def notify_user(title, message, urgency="normal"):
        print(f"[Notification: {urgency}] {title} - {message}")

# === LAUNCH AGENT INSTALLER ===
def ensure_launch_agent_installed(script_path: str):
    username = MAC_USERNAME
    agent_label = "com.myztrix.calendaragent"
    plist_dir = Path.home() / 'Library' / 'LaunchAgents'
    plist_path = plist_dir / f"{agent_label}.plist"
    log_path = Path.home() / 'Library' / 'Logs' / 'myztrix-calendar.log'

    if plist_path.exists():
        logger.info(f"LaunchAgent already installed at {plist_path}")
        return

    plist_dir.mkdir(parents=True, exist_ok=True)

    plist_content = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" 
\"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
  <dict>
    <key>Label</key>
    <string>{agent_label}</string>
    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/python3</string>
      <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{log_path}</string>
    <key>StandardErrorPath</key>
    <string>{log_path}</string>
  </dict>
</plist>
"""
    plist_path.write_text(plist_content)
    logger.info(f"LaunchAgent plist created at {plist_path}")

    try:
        subprocess.run(["launchctl", "unload", str(plist_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["launchctl", "load", str(plist_path)], check=True)
        logger.info("LaunchAgent loaded successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to load LaunchAgent: {e}")
        notify_user(
            title="🔥 LaunchAgent Load Failed 🔥",
            message="Failed to load LaunchAgent plist. Check logs.",
            urgency="critical"
        )

# === AUTHENTICATION ===
def authenticate():
    if not TOKEN_PATH.exists():
        raise FileNotFoundError("Missing token.json. Run OAuth flow first.")

    with open(TOKEN_PATH, 'r') as f:
        creds = Credentials.from_authorized_user_info(json.load(f), scopes=[
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/gmail.readonly"
        ])

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return creds

def get_calendar_service():
    creds = authenticate()
    service = build("calendar", "v3", credentials=creds)
    return service

# === PROCESS EVENTS ===
def process_pending_events():
    try:
        if not PENDING_EVENTS_PATH.exists():
            logger.info("No pending events file found.")
            return

        with open(PENDING_EVENTS_PATH, 'r') as f:
            pending_events = json.load(f)

        if not pending_events:
            logger.info("No pending events to process.")
            return

        service = get_calendar_service()
        successful = []
        local_tz = tzlocal.get_localzone()

        for email_id, event in list(pending_events.items()):
            start_time = datetime.fromisoformat(event['start_time']).astimezone(local_tz)
            end_time = datetime.fromisoformat(event['end_time']).astimezone(local_tz)

            calendar_event = {
                'summary': event['title'],
                'description': event['description'],
                'start': {'dateTime': start_time.isoformat(), 'timeZone': str(local_tz)},
                'end': {'dateTime': end_time.isoformat(), 'timeZone': str(local_tz)},
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 1440},
                        {'method': 'popup', 'minutes': 120},
                        {'method': 'popup', 'minutes': 60},
                        {'method': 'popup', 'minutes': 30},
                    ]
                }
            }

            created_event = service.events().insert(calendarId='primary', body=calendar_event).execute()
            logger.info(f"Created calendar event: {created_event['id']}")
            successful.append(email_id)

        # Remove successfully processed events
        for sid in successful:
            pending_events.pop(sid, None)

        with open(PENDING_EVENTS_PATH, 'w') as f:
            json.dump(pending_events, f, indent=2)

        update_status("success", len(successful))

    except Exception as e:
        logger.error(f"Error creating calendar events: {str(e)}")
        notify_user(
            title="🔥 Calendar Agent Failed 🔥",
            message="Couldn't create one or more calendar events. Check logs.",
            urgency="critical"
        )
        update_status("failure", 0)

# === STATUS UPDATE ===
def update_status(status: str, count: int):
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    status_data = {
        'last_run': datetime.utcnow().isoformat(),
        'status': status,
        'events_created': count
    }
    with open(STATUS_PATH, 'w') as f:
        json.dump(status_data, f, indent=2)

# === FLASK ROUTES ===
@app.route("/process_events", methods=["POST"])
def trigger_event_processor():
    process_pending_events()
    return jsonify({"status": "triggered"})

@app.route("/status", methods=["GET"])
def get_status():
    if STATUS_PATH.exists():
        with open(STATUS_PATH, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({"status": "unknown"})

# === MAIN ===
if __name__ == '__main__':
    import sys
    script_absolute_path = os.path.abspath(sys.argv[0])
    ensure_launch_agent_installed(script_absolute_path)
    app.run(debug=False, port=8888)


