#!/bin/bash
MESSAGE=$1
if [ -z "$MESSAGE" ]; then
  MESSAGE="Pipeline completed successfully."
fi
echo "Notification: $MESSAGE"
