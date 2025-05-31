#!/bin/sh

# Fix permissions in case Synology resets them
chmod -R 775 /data 2>/dev/null || true

# Start watcher for new files
exec python /app/watcher.py
