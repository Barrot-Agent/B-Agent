# Quick Start: Email Intelligence for Barrot

## Simple Usage

### 1. Analyze a Single Email
```python
from email_analyzer import analyze_email

email = {
    "subject": "Meeting tomorrow at 2pm",
    "sender": "manager@company.com",
    "body": "Let's discuss the project. Please confirm attendance.",
    "date": "2025-12-31T10:00:00Z"
}

result = analyze_email(email)
print(f"Useful: {result['is_useful']}")
print(f"Priority: {result['priority']}")
print(f"Recommendation: {result['recommendation']}")
```

### 2. Analyze Multiple Emails
```python
from email_analyzer import analyze_emails

emails = [
    {"subject": "...", "sender": "...", "body": "..."},
    {"subject": "...", "sender": "...", "body": "..."}
]

result = analyze_emails(emails)
print(f"Useful emails: {result['useful_emails']}/{result['total_emails']}")
print(f"High priority: {result['high_priority_count']}")
print(f"Action items: {result['total_action_items']}")
```

### 3. Full Barrot Intelligence (AGI + Quantum)
```python
from barrot_integration import process_emails

result = process_emails(emails)
print(result['intelligence_summary'])
```

## Email Data Format

```python
email = {
    "subject": "Email subject",        # Required
    "sender": "sender@example.com",    # Required  
    "body": "Email body text",         # Required
    "date": "2025-12-31T10:00:00Z",   # Optional
    "attachments": ["file.pdf"]        # Optional
}
```

## Understanding Results

### Usefulness Score
- **0.8-1.0**: Highly useful - immediate attention
- **0.6-0.8**: Useful - review soon
- **0.3-0.6**: Moderately useful - review later
- **0.0-0.3**: Not useful - archive/delete

### Priority Levels
- **HIGH**: Urgent, immediate action needed
- **MEDIUM**: Important, review within 24h
- **LOW**: Low priority, review when convenient
- **NOISE**: Very low value, consider filtering

### Categories
- `action_required` - Has tasks or requests
- `learning_opportunity` - Contains educational content
- `business_opportunity` - Job offers, partnerships
- `intelligence` - Insights, trends, analysis
- `social` - Networking, thank you notes
- `informational` - Updates, newsletters
- `notification` - Automated notifications
- `spam` - Unsolicited promotional content

## Common Use Cases

### Triage Inbox
```python
from email_analyzer import email_analyzer

for email_data in inbox:
    result = email_analyzer.analyze_email(email_data)
    
    if result['priority'] == 'high':
        move_to_folder(email_data, 'Urgent')
    elif 'action_required' in result['categories']:
        move_to_folder(email_data, 'Tasks')
    elif result['is_useful']:
        move_to_folder(email_data, 'Review')
    else:
        move_to_folder(email_data, 'Archive')
```

### Extract Action Items
```python
result = analyze_emails(emails)

for action in result['action_items']:
    print(f"Action: {action['description']}")
    print(f"From: {action['email_sender']}")
    create_task(action['description'])
```

### Find Opportunities
```python
result = analyze_emails(emails)

for opp in result['opportunities']:
    print(f"{opp['type']}: {opp['subject']}")
    notify_user(f"New opportunity: {opp['type']}")
```

## Full Documentation
See [EMAIL_PROCESSING_GUIDE.md](EMAIL_PROCESSING_GUIDE.md) for complete documentation.

## Examples
Run the example scripts:
```bash
python3 example_email_analysis.py
python3 test_email_integration.py
```
