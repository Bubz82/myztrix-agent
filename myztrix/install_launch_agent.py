import os
import subprocess
from pathlib import Path

LAUNCH_AGENT_NAME = "com.myztrix.calendaragent"

def write_plist(plist_path: Path, program_path: str, label: str):
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{label}</string>

  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>{program_path}</string>
  </array>

  <key>RunAtLoad</key>
  <true/>

  <key>KeepAlive</key>
  <true/>

  <key>StandardOutPath</key>
  <string>/tmp/{label}.out.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/{label}.err.log</string>
</dict>
</plist>"""
    plist_path.write_text(plist_content)
    print(f"[✓] Wrote LaunchAgent plist to {plist_path}")

def install_and_load(label: str, program_path: Path):
    user_home = Path.home()
    launch_agents_dir = user_home / "Library" / "LaunchAgents"
    launch_agents_dir.mkdir(parents=True, exist_ok=True)

    plist_path = launch_agents_dir / f"{label}.plist"
    write_plist(plist_path, str(program_path), label)

    subprocess.run(["launchctl", "unload", str(plist_path)], stderr=subprocess.DEVNULL)
    subprocess.run(["launchctl", "load", str(plist_path)], check=True)

    print(f"[✓] Loaded LaunchAgent: {label}")

def main():
    user_home = Path.home()
    agent_script = user_home / "myztrix" / "calendar_agent.py"

    if not agent_script.exists():
        print(f"[!] calendar_agent.py not found at {agent_script}")
        return

    install_and_load(LAUNCH_AGENT_NAME, agent_script)

if __name__ == "__main__":
    main()
