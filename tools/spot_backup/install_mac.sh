#!/bin/bash
# Installs the hourly launchd job for the spot backup (runs at login + every hour; copies only when 48 h passed).
# Usage: bash tools/spot_backup/install_mac.sh      Remove: launchctl unload ~/Library/LaunchAgents/com.xpix.spotbackup.plist
set -e
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
PY="$(command -v python3)"
PL="$HOME/Library/LaunchAgents/com.xpix.spotbackup.plist"
"$PY" -c "import openpyxl, requests" 2>/dev/null || "$PY" -m pip install --user openpyxl requests pandas
if [ ! -f "$HOME/.xpix_spot_backup.env" ]; then
  printf 'SPOT_GH_TOKEN=\nSPOT_GH_REPO=\nSPOT_BACKUP_DIR=~/XPiX-Spot-Backup\nSPOT_BACKUP_HOURS=48\nSPOT_BACKUP_KEEP=1\n' > "$HOME/.xpix_spot_backup.env"
  chmod 600 "$HOME/.xpix_spot_backup.env"
  echo "Fill SPOT_GH_TOKEN and SPOT_GH_REPO in ~/.xpix_spot_backup.env, then run this again."
fi
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
cat > "$PL" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.xpix.spotbackup</string>
  <key>ProgramArguments</key><array><string>$PY</string><string>$REPO/tools/spot_backup/spot_backup.py</string></array>
  <key>StartInterval</key><integer>3600</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$HOME/Library/Logs/xpix_spot_backup.log</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/xpix_spot_backup.log</string>
</dict></plist>
PLIST
launchctl unload "$PL" 2>/dev/null || true
launchctl load "$PL"
echo "Installed. First copy: python3 $REPO/tools/spot_backup/spot_backup.py --now   Log: ~/Library/Logs/xpix_spot_backup.log"
