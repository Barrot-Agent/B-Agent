#!/bin/bash
JOB_NAME=$1
MAX_RETRIES=3
COUNT=0

while [ $COUNT -lt $MAX_RETRIES ]; do
  echo "Retrying $JOB_NAME (Attempt $((COUNT+1)))..."
  if ./scripts/$JOB_NAME.sh; then
    echo "$JOB_NAME succeeded on attempt $((COUNT+1))"
    exit 0
  fi
  COUNT=$((COUNT+1))
  sleep $((COUNT*10)) # Exponential backoff
done

echo "$JOB_NAME failed after $MAX_RETRIES attempts"
./scripts/barrot-notify.sh "Pipeline $JOB_NAME failed after retries"
exit 1
