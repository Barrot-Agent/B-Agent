# Ping-Pong Request System

## Overview

The `emit_pingpong_request` function allows Barrot-Agent to defer complex processing tasks to Sean's 22-agent entanglement system.

## Usage

```python
from emit_pingpong import emit_pingpong_request

# Create your payload
payload = {
    "task": "process_quantum_data",
    "priority": "high",
    "data": {"items": [1, 2, 3]}
}

# Emit the request
emit_pingpong_request(payload)
```

## Output

The function creates a `pingpong_request.json` file with the following structure:

```json
{
  "timestamp": "2025-12-30T11:39:52.503571+00:00",
  "payload": { ... },
  "origin": "barrot",
  "directive": "offload_pingpong",
  "notes": "Barrot defers to Sean's 22-agent entanglement system."
}
```

## Workflow

1. Call `emit_pingpong_request(payload)` with your data
2. The function generates `pingpong_request.json`
3. Commit the JSON file to GitHub
4. The external system (Sean's 22-agent entanglement system) picks up the request
5. Processing is offloaded to the external system

## Notes

- The generated `pingpong_request.json` file is excluded from version control by default (see `.gitignore`)
- To trigger the external system, you must manually commit and push the JSON file
- Timestamps are in ISO 8601 format with UTC timezone
## SMS webhook adapter

`scripts/barrot_sms_webhook.py` provides a dependency-free Twilio-compatible
inbound webhook and routes authorized messages through the existing
`scripts/pingpong.py` chain (including its optional GPT cross-check).

Configure these deployment-only environment variables:

- `TWILIO_AUTH_TOKEN`
- `BARROT_SMS_ALLOWED_FROM` (comma-separated E.164 sender numbers)
- `BARROT_SMS_PUBLIC_URL` (the exact public webhook URL used for signature validation)
- Optional `BARROT_SMS_BIND` and `BARROT_SMS_PORT`

The adapter rejects invalid signatures and non-allow-listed senders, prevents
replay and rate abuse, bounds replies, redacts request logging, and returns a
generic failure response when the Barrot chain is unavailable. Keep credentials
in the hosting provider's secret store; never commit them. Twilio must be
configured to POST URL-encoded messages to the deployed endpoint.

### T-Mobile/Termux alternative

Twilio is not required when an Android phone with the T-Mobile SIM is
available. Install Termux and Termux:API from a trusted source, grant SMS
permissions, and run `scripts/termux_sms_bridge.py` with:

- `BARROT_SMS_ENDPOINT`: the Barrot HTTPS JSON endpoint
- `BARROT_SMS_SHARED_SECRET`: a deployment-only random secret
- `BARROT_SMS_REPLY_TO`: the phone number that receives replies

The bridge polls `termux-sms-list`, forwards new messages with an HMAC
signature, and sends the response using `termux-sms-send`. Configure these
variables in Termux's private environment, not in Git. The repository cannot
activate the T-Mobile line, install Android apps, grant permissions, or verify
delivery; those steps require the physical phone and a reachable HTTPS
deployment.
