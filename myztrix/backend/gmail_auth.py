import os
import json
import pathlib
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

def run_oauth_flow():
    creds_path = pathlib.Path(__file__).parent.parent / 'credentials' / 'credentials.json'
    if not creds_path.exists():
        raise FileNotFoundError(f"Credentials file not found at {creds_path}")

    flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
    creds = flow.run_local_server(port=0)

    token_path = pathlib.Path(__file__).parent / 'token.json'  # token saved here
    with open(token_path, 'w') as token_file:
        token_file.write(creds.to_json())
    print(f"✅ Token saved to {token_path}")

if __name__ == '__main__':
    run_oauth_flow()