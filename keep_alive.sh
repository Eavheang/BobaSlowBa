#!/bin/sh

# Run the keep-alive script every 14 minutes
while true; do
    python /app/keep_alive.py
    sleep 840  # 14 minutes in seconds
done