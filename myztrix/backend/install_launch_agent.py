import os
import getpass
from pathlib import Path
import subprocess
import sys

def install_launch_agent():
    try:
        username = getpass.getuser()
        agent_label = "com.myztrix.calendaragent"
        plist_path = Path(f"/Users/{username}/Library/LaunchAgents/{agent_label}.plist")
        log_path = Path(f"/Users/{username}/Library/Logs/myztrix-calendar.log")

        # TODO: Replace this with the actual absolute path on the Mac where calendar_agent.py will live
        script_path = Path("/absolute/path/to/calendar_agent.py")

        if not script_path.exists():
            print(f"[!] ERROR: calendar_agent.py not found at {script_path}")
            sys.exit(1)

        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>{agent_label}</string>

    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/python3</string>
      <string>{script_path}</string>
    </array>

    <key>StartInterval</key>
    <integer>600</integer>

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

        # Ensure LaunchAgents directory exists
        plist_path.parent.mkdir(parents=True, exist_ok=True)
        # Ensure Logs directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the plist file
        plist_path.write_text(plist_content)
        print(f"[+] LaunchAgent plist written to {plist_path}")

        # Unload if already loaded (avoid duplicates/errors)
        subprocess.run(["launchctl", "unload", str(plist_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Load the LaunchAgent
        result = subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True, text=True)

        if result.returncode == 0:
            print("[+] LaunchAgent loaded successfully.")
        else:
            print(f"[!] ERROR loading LaunchAgent: {result.stderr.strip()}")
            sys.exit(1)

    except Exception as e:
        print(f"[!] Exception during install_launch_agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_launch_agent()
