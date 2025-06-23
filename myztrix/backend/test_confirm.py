import requests
import json
import socket
import time

def check_server_running(host, port):
    """Check if a server is running on the given host and port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

# Check if the server is running
if not check_server_running("127.0.0.1", 5000):
    print("Server is not running on http://127.0.0.1:5000")
    print("Please start the server with: python main.py")
    exit(1)

url = "http://127.0.0.1:5000/confirm"
headers = {"Content-Type": "application/json"}
data = {
    "summary": "Agent War Room Briefing",
    "description": "Prep meeting before operations",
    "location": "HQ Conference Room",
    "start_time": "2025-06-12T10:00:00",
    "end_time": "2025-06-12T11:00:00"
}

try:
    print("Sending request to:", url)
    print("With data:", json.dumps(data, indent=2))
    
    # Set a timeout for the request
    response = requests.post(url, headers=headers, json=data, timeout=10)
    
    print("Status code:", response.status_code)
    print("Response:", response.text)
    
    if response.status_code == 200:
        print("Success! Event created.")
    else:
        print(f"Failed with status code: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("Connection error. Make sure the server is running.")
except requests.exceptions.Timeout:
    print("Request timed out. The server might be busy or not responding.")
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
