import os
import json
import socket
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# OAuth 2.0 scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar'
]

def find_free_port():
    """Find a free port to use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def test_oauth_flow():
    """Demonstrate the Google OAuth login flow."""
    credentials_path = os.path.join('credentials', 'client_secrets.json')
    token_path = os.path.join('credentials', 'token.json')
    
    print("\n=== Google OAuth Login Flow Test ===")
    print("\nStep 1: Checking for existing credentials...")
    
    # Check if we have a token file
    if os.path.exists(token_path):
        print("Found existing token file.")
        with open(token_path, 'r') as token:
            credentials = Credentials.from_authorized_user_info(
                json.load(token), SCOPES
            )
            
        if credentials and credentials.valid:
            print("Existing credentials are valid!")
            return credentials
            
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing expired credentials...")
            credentials.refresh(Request())
    else:
        print("No existing token found. Starting new authentication flow...")
    
    print("\nStep 2: Starting OAuth flow...")
    
    # Find a free port
    port = find_free_port()
    print(f"Using port: {port}")
    
    # Start the OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        credentials_path, SCOPES
    )
    
    # Get the authorization URL
    auth_url, _ = flow.authorization_url()
    print(f"\nAuthorization URL: {auth_url}")
    print("\nPlease:")
    print("1. Copy the URL above")
    print("2. Open it in your browser")
    print("3. Log in to your Google account")
    print("4. Grant the requested permissions")
    
    try:
        credentials = flow.run_local_server(
            port=port,
            prompt='consent',
            authorization_prompt_message='Please visit this URL to authorize the application: {url}',
            success_message='The authentication flow has completed. You may close this window.'
        )
        
        # Save the credentials
        print("\nStep 3: Saving credentials...")
        with open(token_path, 'w') as token:
            token.write(credentials.to_json())
        
        print("\nAuthentication successful!")
        print("Credentials have been saved to:", token_path)
        return credentials
        
    except Exception as e:
        print(f"\nError during authentication: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure no other application is using the port")
        print("2. Try closing and reopening your browser")
        print("3. Check if your firewall is blocking the connection")
        print("4. Try running the script again")
        raise

if __name__ == "__main__":
    try:
        if not os.path.exists('credentials/client_secrets.json'):
            print("\nError: client_secrets.json not found!")
            print("Please make sure you have:")
            print("1. Created a project in Google Cloud Console")
            print("2. Enabled Gmail and Calendar APIs")
            print("3. Created OAuth 2.0 credentials")
            print("4. Downloaded and placed client_secrets.json in the credentials folder")
            exit(1)
            
        credentials = test_oauth_flow()
        print("\nYou can now run the main test script:")
        print("python test_agent.py")
    except Exception as e:
        print(f"\nError during authentication: {str(e)}")
        print("\nPlease make sure:")
        print("1. You have placed client_secrets.json in the credentials folder")
        print("2. You have enabled the Gmail and Calendar APIs in Google Cloud Console")
        print("3. Your Google account has access to Gmail and Calendar") 