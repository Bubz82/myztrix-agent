import subprocess
import time
from pathlib import Path

LAUNCH_AGENT_NAME = "com.myztrix.calendaragent"

def is_agent_loaded():
    result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    return LAUNCH_AGENT_NAME in result.stdout

def reload_agent():
    user_home = Path.home()
    plist_path = user_home / "Library" / "LaunchAgents" / f"{LAUNCH_AGENT_NAME}.plist"
    subprocess.run(["launchctl", "load", "-w", str(plist_path)])

def watchdog_loop():
    while True:
        if not is_agent_loaded():
            print(f"[Watchdog] Agent not loaded, reloading...")
            reload_agent()
        time.sleep(300)  # check every 5 minutes

if __name__ == "__main__":
    watchdog_loop()