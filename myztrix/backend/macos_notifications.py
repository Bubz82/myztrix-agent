import os
import json
import subprocess
from typing import Dict, Optional

class MacOSNotifier:
    def __init__(self, pending_events_path: str, declined_events_path: str):
        self.pending_events_path = pending_events_path
        self.declined_events_path = declined_events_path

    def _load_json_file(self, file_path: str, default: dict = None) -> dict:
        """Load JSON file or return default if file doesn't exist."""
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return default or {}

    def _save_json_file(self, file_path: str, data: dict):
        """Save data to JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def send_notification(self, email_id: str, event_details: Dict) -> bool:
        """
        Send a macOS notification with Add/Dismiss buttons for an event.
        Returns True if notification was sent successfully.
        """
        try:
            # Create AppleScript for notification
            title = event_details['title']
            description = event_details['description'][:100] + "..." if len(event_details['description']) > 100 else event_details['description']
            start_time = event_details['start_time']
            
            # Create a unique identifier for this notification
            notification_id = f"gmail_event_{email_id}"
            
            # AppleScript for notification with buttons
            script = f'''
            tell application "System Events"
                set notificationTitle to "{title}"
                set notificationBody to "{description}"
                set notificationTime to "{start_time}"
                
                display dialog notificationBody & return & return & "Start Time: " & notificationTime buttons {{"Add to Calendar", "Dismiss"}} default button "Add to Calendar" with title notificationTitle
                
                set buttonPressed to button returned of result
                
                if buttonPressed is "Add to Calendar" then
                    do shell script "echo 'add' > /tmp/{notification_id}_response"
                else
                    do shell script "echo 'dismiss' > /tmp/{notification_id}_response"
                end if
            end tell
            '''
            
            # Execute AppleScript
            subprocess.run(['osascript', '-e', script], check=True)
            
            # Wait for response file
            response_file = f"/tmp/{notification_id}_response"
            if os.path.exists(response_file):
                with open(response_file, 'r') as f:
                    response = f.read().strip()
                os.remove(response_file)
                
                if response == 'add':
                    # Move to pending events
                    pending_events = self._load_json_file(self.pending_events_path, {})
                    pending_events[email_id] = event_details
                    self._save_json_file(self.pending_events_path, pending_events)
                    return True
                elif response == 'dismiss':
                    # Move to declined events
                    declined_events = self._load_json_file(self.declined_events_path, {})
                    declined_events[email_id] = event_details
                    self._save_json_file(self.declined_events_path, declined_events)
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            return False

    def process_pending_events(self) -> None:
        """Process any pending events that haven't been shown as notifications yet."""
        pending_events = self._load_json_file(self.pending_events_path, {})
        for email_id, event_details in list(pending_events.items()):
            if self.send_notification(email_id, event_details):
                # Remove from pending if notification was sent successfully
                del pending_events[email_id]
                self._save_json_file(self.pending_events_path, pending_events) 