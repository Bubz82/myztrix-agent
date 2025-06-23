# Mac Gmail Calendar Agent

A lightweight macOS agent that automatically detects events in Gmail and creates calendar events with layered reminders.

## Features

- Polls Gmail for unread emails every 5 minutes
- Uses NLP to detect event-related emails
- Shows native macOS notifications with Add/Dismiss buttons
- Creates Google Calendar events with layered reminders:
  - Email notification 1 day before
  - Popup notifications at 2 hours, 1 hour, and 30 minutes before
- Labels declined events in Gmail
- Runs automatically on system startup
- Lightweight and native macOS integration

## Prerequisites

- Python 3.7 or higher
- macOS 10.13 or higher (for production)
- Google account with Gmail and Calendar access

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd gmail-calendar-agent
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google Cloud Project and OAuth credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable Gmail API and Google Calendar API
   - Create OAuth 2.0 credentials
   - Download the credentials and save as `credentials/client_secrets.json`

4. Install the launch agent for automatic startup (macOS only):
```bash
python install_launch_agent.py
```

## Testing on Windows

While this agent is designed for macOS, you can test its core functionality on Windows using the test script:

1. Run the test script:
```bash
python test_agent.py
```

The test script will:
- Simulate the Mac notification system using console input
- Use sample email data to test event detection
- Allow you to test the calendar integration
- Show you how the agent would work on macOS

The test environment includes:
- Console-based notifications instead of native Mac notifications
- Sample email data for testing
- Same event detection and calendar integration as the Mac version
- 30-second polling interval (instead of 5 minutes) for faster testing

## Usage

### On macOS:
The agent will start automatically on system login. To manage the agent:

- Start manually:
```bash
python run_agent.py
```

- Uninstall launch agent:
```bash
python install_launch_agent.py --uninstall
```

### On Windows (Testing):
- Run the test script:
```bash
python test_agent.py
```

- Press Ctrl+C to stop the test at any time

## Configuration

The agent uses the following files for configuration and state:

- `credentials/client_secrets.json`: Google OAuth credentials
- `credentials/token.json`: OAuth token (created automatically)
- `pending_events.json`: Events waiting to be added to calendar
- `declined_events.json`: Events that were dismissed
- `gmail_agent.log`: Application logs
- `test_agent.log`: Test environment logs (Windows testing)
- `launch_agent_error.log`: Launch agent error logs (macOS only)
- `launch_agent_output.log`: Launch agent output logs (macOS only)

## Troubleshooting

1. If the agent fails to start:
   - Check `gmail_agent.log` for errors
   - Verify OAuth credentials are correct
   - Ensure all dependencies are installed

2. If notifications aren't working:
   - On macOS: Check System Preferences > Notifications
   - On Windows: Ensure you're using the test script
   - Check logs for specific errors

3. If calendar events aren't being created:
   - Check Google Calendar API is enabled
   - Verify OAuth token has calendar permissions
   - Check logs for specific errors

## Uninstallation

1. Stop the agent:
   - On macOS: `python install_launch_agent.py --uninstall`
   - On Windows: Press Ctrl+C in the test script

2. Remove the project directory:
```bash
rm -rf gmail-calendar-agent
```

## License

MIT License 