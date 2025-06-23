import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
token_path = os.path.join(BASE_DIR, 'credentials', 'token.json')
cred_path = os.path.join(BASE_DIR, 'credentials', 'credentials.json')

print(f"Token.json exists? {os.path.exists(token_path)} at {token_path}")
print(f"Credentials.json exists? {os.path.exists(cred_path)} at {cred_path}")
