import os
import shutil
import logging
from gmail_agent import check_emails
from calendar_handler import get_calendar_service

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Step 1: Define secure storage path ===
APPDATA_PATH = os.path.join(os.environ.get('APPDATA'), 'MyztrixAgent')
CREDENTIALS_PATH = os.path.join(APPDATA_PATH, 'credentials.json')
TOKEN_PATH = os.path.join(APPDATA_PATH, 'token.json')

# === Step 2: Ensure secure storage folder exists ===
os.makedirs(APPDATA_PATH, exist_ok=True)

# === Step 3: Copy credentials.json once then remove source ===
SOURCE_CRED = os.path.join(os.path.dirname(__file__), 'credentials', 'credentials.json')

if os.path.exists(SOURCE_CRED) and not os.path.exists(CREDENTIALS_PATH):
    try:
        shutil.copy2(SOURCE_CRED, CREDENTIALS_PATH)
        os.remove(SOURCE_CRED)
        logger.info(f"Moved credentials.json to secure location: {CREDENTIALS_PATH}")
    except Exception as e:
        logger.error(f"Failed to move credentials file: {e}")
        exit(1)

# === Step 4: Run main Gmail agent logic ===
def main():
    logger.info("Starting Gmail agent daemon")
    try:
        check_emails(CREDENTIALS_PATH, TOKEN_PATH)
    except Exception as e:
        logger.error(f"Error in check_emails: {e}")

if __name__ == '__main__':
    main()

