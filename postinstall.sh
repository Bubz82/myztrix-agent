#!/bin/bash

# Get the currently logged-in user (not root)
current_user=$(stat -f "%Su" /dev/console)
user_home=$(dscl . -read /Users/"$current_user" NFSHomeDirectory | awk '{print $2}')

plist_source_path="${INSTALL_DIR}/com.myztrix.calendaragent.plist"
plist_target_path="$user_home/Library/LaunchAgents/com.myztrix.calendaragent.plist"

echo "Running postinstall script for user: $current_user"

# Create LaunchAgents folder if missing
mkdir -p "$user_home/Library/LaunchAgents"

# Replace USERNAME with actual user in .plist before copying
sed -i '' "s/USERNAME/$current_user/g" "$plist_source_path"

# Copy the plist file to LaunchAgents folder
cp "$plist_source_path" "$plist_target_path"
chown "$current_user":staff "$plist_target_path"
chmod 644 "$plist_target_path"

# Load the launch agent for the user
sudo -u "$current_user" launchctl unload "$plist_target_path" 2>/dev/null
sudo -u "$current_user" launchctl load "$plist_target_path"

echo "Launch agent installed and loaded."
exit 0


