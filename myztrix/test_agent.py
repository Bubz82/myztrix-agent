import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from backend.gmail_agent import GmailAgent
from backend.calendar_manager import CalendarManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MockMacOSNotifier:
    """Mock implementation of MacOS notifications for Windows testing."""
    def __init__(self, pending_events_path: str, declined_events_path: str):
        self.pending_events_path = pending_events_path
        self.declined_events_path = declined_events_path

    def _load_json_file(self, file_path: str, default: dict = None) -> dict:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return default or {}

    def _save_json_file(self, file_path: str, data: dict):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def send_notification(self, email_id: str, event_details: Dict) -> bool:
        """Simulate MacOS notification with console input."""
        try:
            print("\n" + "="*50)
            print("EVENT DETECTED:")
            print(f"Title: {event_details['title']}")
            print(f"Description: {event_details['description'][:100]}...")
            print(f"Start Time: {event_details['start_time']}")
            print("="*50)
            
            while True:
                response = input("\nWould you like to add this event to your calendar? (yes/no): ").lower()
                if response in ['yes', 'no']:
                    break
                print("Please enter 'yes' or 'no'")

            if response == 'yes':
                # Move to pending events
                pending_events = self._load_json_file(self.pending_events_path, {})
                pending_events[email_id] = event_details
                self._save_json_file(self.pending_events_path, pending_events)
                print("Event added to pending events.")
                return True
            else:
                # Move to declined events
                declined_events = self._load_json_file(self.declined_events_path, {})
                declined_events[email_id] = event_details
                self._save_json_file(self.declined_events_path, declined_events)
                print("Event marked as declined.")
                return True

        except Exception as e:
            logger.error(f"Error in mock notification: {str(e)}")
            return False

    def process_pending_events(self) -> None:
        """Process any pending events that haven't been shown as notifications yet."""
        pending_events = self._load_json_file(self.pending_events_path, {})
        for email_id, event_details in list(pending_events.items()):
            if self.send_notification(email_id, event_details):
                del pending_events[email_id]
                self._save_json_file(self.pending_events_path, pending_events)

def test_with_sample_data():
    """Test the agent with sample email data."""
    # Sample email data
    sample_emails = [
        {
            'id': '1',
            'subject': 'Team Meeting Tomorrow',
            'sender': 'boss@company.com',
            'date': datetime.now().isoformat(),
            'body': 'Hi team, let\'s meet tomorrow at 2 PM to discuss the project progress. Please bring your updates.'
        },
        {
            'id': '2',
            'subject': 'Project Deadline Reminder',
            'sender': 'project@company.com',
            'date': datetime.now().isoformat(),
            'body': 'The project deadline is next Monday at 5 PM. Make sure all deliverables are ready.'
        },
        {
            'id': '3',
            'subject': 'Weekly Sync',
            'sender': 'team@company.com',
            'date': datetime.now().isoformat(),
            'body': 'Our weekly sync is scheduled for Friday at 10 AM. Agenda will be shared soon.'
        }
    ]

    # Initialize services
    agent = GmailAgent('credentials/client_secrets.json', 'credentials/token.json')
    notifier = MockMacOSNotifier('pending_events.json', 'declined_events.json')
    calendar = CalendarManager('credentials/client_secrets.json', 'credentials/token.json')

    print("\nTesting Gmail Calendar Agent...")
    print("This is a simulation of the Mac agent running on Windows.")
    print("You'll be able to test the event detection and notification system.")
    print("\nPress Ctrl+C to stop the test at any time.")

    try:
        while True:
            print("\nChecking for new emails...")
            
            for email in sample_emails:
                # Detect event
                is_event, confidence, event_details = agent.detect_event(email)
                
                if is_event and confidence >= 0.6:
                    logger.info(f"Detected event in email: {email['subject']} (confidence: {confidence:.2f})")
                    
                    # Send notification
                    if notifier.send_notification(email['id'], event_details):
                        if email['id'] in json.load(open('declined_events.json', 'r')):
                            print(f"Email {email['id']} marked as declined")
                        else:
                            print(f"Email {email['id']} added to pending events")
                else:
                    print(f"No event detected in email: {email['subject']}")

            # Process any pending events for calendar creation
            calendar.process_pending_events('pending_events.json')
            
            print("\nWaiting 30 seconds before next check...")
            time.sleep(30)

    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")

if __name__ == "__main__":
    test_with_sample_data() 