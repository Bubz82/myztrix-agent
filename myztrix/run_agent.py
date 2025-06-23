import os
import time
import json
import logging
import schedule
from datetime import datetime
from backend.gmail_agent import GmailAgent
from backend.macos_notifications import MacOSNotifier
from backend.calendar_manager import CalendarManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gmail_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CREDENTIALS_PATH = os.path.join('credentials', 'client_secrets.json')
TOKEN_PATH = os.path.join('credentials', 'token.json')
PENDING_EVENTS_PATH = 'pending_events.json'
DECLINED_EVENTS_PATH = 'declined_events.json'

def load_json_file(file_path: str, default: dict = None) -> dict:
    """Load JSON file or return default if file doesn't exist."""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return default or {}

def save_json_file(file_path: str, data: dict):
    """Save data to JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def check_emails():
    """Check for new emails and detect events."""
    try:
        # Load existing events
        pending_events = load_json_file(PENDING_EVENTS_PATH, {})
        declined_events = load_json_file(DECLINED_EVENTS_PATH, {})
        
        # Initialize services
        agent = GmailAgent(CREDENTIALS_PATH, TOKEN_PATH)
        notifier = MacOSNotifier(PENDING_EVENTS_PATH, DECLINED_EVENTS_PATH)
        calendar = CalendarManager(CREDENTIALS_PATH, TOKEN_PATH)
        
        if not agent.authenticate():
            logger.error("Failed to authenticate with Gmail")
            return
        
        # Get unread emails
        emails = agent.get_unread_emails()
        logger.info(f"Found {len(emails)} unread emails")
        
        for email in emails:
            # Skip if email already processed
            if email['id'] in pending_events or email['id'] in declined_events:
                continue
            
            # Detect event
            is_event, confidence, event_details = agent.detect_event(email)
            
            if is_event and confidence >= 0.6:
                logger.info(f"Detected event in email: {email['subject']} (confidence: {confidence:.2f})")
                
                # Send notification
                if notifier.send_notification(email['id'], event_details):
                    # Mark email as read if notification was sent successfully
                    agent.mark_as_read(email['id'])
                    
                    if email['id'] in declined_events:
                        # Add declined label if user dismissed
                        agent.add_label(email['id'], 'Declined')
            else:
                # Mark non-event emails as read
                agent.mark_as_read(email['id'])
        
        # Process any pending events that haven't been shown as notifications
        notifier.process_pending_events()
        
        # Process any pending events for calendar creation
        calendar.process_pending_events(PENDING_EVENTS_PATH)
        
    except Exception as e:
        logger.error(f"Error in check_emails: {str(e)}")

def main():
    """Main function to run the Gmail agent daemon."""
    logger.info("Starting Gmail agent daemon")
    
    # Schedule email checks every 5 minutes
    schedule.every(5).minutes.do(check_emails)
    
    # Run initial check
    check_emails()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main() 