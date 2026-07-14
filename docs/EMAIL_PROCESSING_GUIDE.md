# 📧 Email Intelligence Processing Guide

## Overview
Barrot-Agent now includes powerful email intelligence processing capabilities that analyze emails to extract useful and actionable information. This feature helps Barrot understand what emails are relevant to his goals and what actions need to be taken.

## Features

### Core Capabilities
1. **Content Analysis** - Parse and understand email content, subject lines, and metadata
2. **Relevance Scoring** - Calculate usefulness scores (0.0 to 1.0) based on content
3. **Action Extraction** - Identify tasks, requests, and deadlines
4. **Opportunity Detection** - Find job offers, partnerships, and business opportunities
5. **Learning Content Detection** - Identify educational content and technical resources
6. **Spam Filtering** - Automatically detect and filter spam/promotional content
7. **Priority Ranking** - Classify emails as HIGH, MEDIUM, LOW, or NOISE priority
8. **Resource Extraction** - Extract URLs, documents, and references from emails
9. **AGI Integration** - Deep contextual understanding using AGI reasoning
10. **Quantum Optimization** - Prioritize actions using quantum entanglement principles

### Email Categories
Barrot categorizes emails into:
- **Action Required** - Emails with tasks, requests, or deadlines
- **Learning Opportunity** - Technical content, tutorials, documentation
- **Business Opportunity** - Jobs, partnerships, consulting offers
- **Intelligence** - Market trends, competitor info, industry insights
- **Social** - Thank you notes, congratulations, networking
- **Informational** - Updates, newsletters, general information
- **Notification** - Automated system notifications
- **Spam** - Unsolicited promotional content

## Quick Start

### Basic Email Analysis
```python
from email_analyzer import analyze_email

# Analyze a single email
email = {
    "subject": "Project deadline approaching",
    "sender": "manager@company.com",
    "body": "Please complete the report by Friday.",
    "date": "2025-12-31T10:00:00Z",
    "attachments": []
}

result = analyze_email(email)
print(f"Priority: {result['priority']}")
print(f"Usefulness Score: {result['usefulness_score']}")
print(f"Categories: {result['categories']}")
print(f"Recommendation: {result['recommendation']}")
```

### Batch Email Analysis
```python
from email_analyzer import analyze_emails

# Analyze multiple emails
emails = [
    {"subject": "Meeting tomorrow", "sender": "colleague@company.com", ...},
    {"subject": "Newsletter", "sender": "news@blog.com", ...},
    {"subject": "Job opportunity", "sender": "recruiter@tech.com", ...}
]

result = analyze_emails(emails)
print(f"Total: {result['total_emails']}")
print(f"Useful: {result['useful_emails']}")
print(f"Summary: {result['summary']}")
```

### Integrated AGI + Quantum Processing
```python
from barrot_integration import process_emails

# Process emails with full Barrot intelligence
emails = [...]  # Your email list

result = process_emails(emails)
print(result['intelligence_summary'])
print(f"AGI Insights: {len(result['agi_insights'])}")
print(f"Quantum Prioritization: {result['quantum_prioritization']}")
```

## Email Data Format

Emails should be provided as dictionaries with the following structure:

```python
email = {
    "id": "unique_email_id",           # Optional: unique identifier
    "subject": "Email subject line",    # Required: subject line
    "sender": "sender@example.com",     # Required: sender email address
    "body": "Email body content...",    # Required: email body text
    "date": "2025-12-31T10:00:00Z",    # Optional: ISO 8601 timestamp
    "attachments": ["file1.pdf", ...]  # Optional: list of attachment names
}
```

## Understanding Results

### Usefulness Score
- **0.0 - 0.3**: Not useful - Archive or delete
- **0.3 - 0.6**: Moderately useful - Review when convenient
- **0.6 - 0.8**: Useful - Review soon
- **0.8 - 1.0**: Highly useful - Priority attention

### Priority Levels
- **HIGH**: Urgent action required, immediate attention needed
- **MEDIUM**: Important but not urgent, review within 24 hours
- **LOW**: Low priority, review when convenient
- **NOISE**: Very low value, consider filtering

### Analysis Results Structure
```python
{
    "email_id": "email_001",
    "subject": "...",
    "sender": "...",
    "priority": "high",
    "categories": ["action_required", "learning_opportunity"],
    "usefulness_score": 0.85,
    "is_useful": true,
    "action_items": [
        {
            "description": "Complete report by Friday",
            "context": "extracted from email body"
        }
    ],
    "learning_content": [
        {
            "type": "technical_content",
            "source": "email_body",
            "relevance": "high"
        }
    ],
    "opportunities": [
        {
            "type": "job",
            "subject": "Senior Engineer position",
            "potential": "medium"
        }
    ],
    "resources": [
        {
            "url": "https://example.com/docs",
            "type": "documentation"
        }
    ],
    "recommendation": "Action required - 2 item(s) need attention"
}
```

## Integration Examples

### Daily Email Processing Workflow
```python
from barrot_integration import process_emails
from datetime import datetime

# Fetch emails from the last 24 hours
emails = fetch_recent_emails(since="24h")

# Process with Barrot's intelligence
result = process_emails(emails)

# Handle high priority items
for email in result['email_analysis']['high_priority_emails']:
    print(f"HIGH PRIORITY: {email['subject']}")
    for action in email['action_items']:
        schedule_task(action['description'])

# Review opportunities
for opp in result['email_analysis']['opportunities']:
    notify_user(f"New {opp['type']} opportunity: {opp['subject']}")

# Store learning content for later
for email in result['email_analysis']['detailed_analyses']:
    if 'learning_opportunity' in email['categories']:
        save_to_learning_queue(email)
```

### Automated Email Triage
```python
from email_analyzer import email_analyzer

def triage_inbox(emails):
    """Automatically triage emails into folders"""
    for email_data in emails:
        analysis = email_analyzer.analyze_email(email_data)
        
        if analysis['priority'] == 'high':
            move_to_folder(email_data, 'Urgent')
        elif 'action_required' in analysis['categories']:
            move_to_folder(email_data, 'Action Items')
        elif 'learning_opportunity' in analysis['categories']:
            move_to_folder(email_data, 'Learning')
        elif 'business_opportunity' in analysis['categories']:
            move_to_folder(email_data, 'Opportunities')
        elif analysis['is_useful']:
            move_to_folder(email_data, 'Review')
        else:
            move_to_folder(email_data, 'Archive')
```

### Export Analysis Report
```python
from email_analyzer import email_analyzer

# After analyzing emails, export a report
email_analyzer.export_analysis_report("daily_email_report.json")

# The report includes:
# - All analyzed emails
# - Statistics and summaries
# - Timestamp of analysis
```

## Privacy & Security

### Important Considerations
1. **Secure Credentials**: Use secure methods to store email credentials
2. **Data Encryption**: Email content should be encrypted during processing
3. **No Permanent Storage**: Sensitive email content is not permanently stored
4. **User Consent**: Always obtain user consent before accessing emails
5. **Compliance**: Follow GDPR, CCPA, and other privacy regulations
6. **Local Processing**: Email analysis happens locally, not sent to external servers

### Best Practices
```python
# Use environment variables for credentials
import os
email_password = os.getenv('EMAIL_PASSWORD')

# Don't log sensitive content
# Don't store raw email bodies permanently
# Use encryption for any temporary storage
# Clear analysis history when done
email_analyzer.analysis_history.clear()
```

## Connecting to Email Services

### Gmail (using IMAP)
```python
import imaplib
import email
from email.header import decode_header

def fetch_gmail_emails(username, password, limit=10):
    """Fetch recent emails from Gmail"""
    # Connect to Gmail
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, password)
    imap.select("INBOX")
    
    # Search for emails
    _, message_numbers = imap.search(None, "UNSEEN")
    
    emails = []
    for num in message_numbers[0].split()[:limit]:
        _, msg_data = imap.fetch(num, "(RFC822)")
        email_body = msg_data[0][1]
        message = email.message_from_bytes(email_body)
        
        # Extract email data
        subject = decode_header(message["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        
        sender = message.get("From")
        date = message.get("Date")
        
        # Get body
        body = ""
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = message.get_payload(decode=True).decode()
        
        emails.append({
            "subject": subject,
            "sender": sender,
            "body": body,
            "date": date
        })
    
    imap.close()
    imap.logout()
    
    return emails

# Usage
emails = fetch_gmail_emails("your_email@gmail.com", "your_app_password")
result = analyze_emails(emails)
```

**Note**: For Gmail, you need to:
1. Enable IMAP in Gmail settings
2. Generate an App Password (not your regular password)
3. Use the App Password in your script

## Advanced Features

### Custom Pattern Matching
You can extend the analyzer with custom patterns:

```python
from email_analyzer import email_analyzer

# Add custom action patterns
custom_patterns = [
    r'\b(deploy|release|ship)\b',
    r'\b(review\s+pr|pull\s+request)\b'
]
email_analyzer.action_patterns.extend(custom_patterns)

# Add custom opportunity keywords
email_analyzer.opportunity_keywords['open_source'] = [
    'contribute', 'open source', 'github', 'pull request'
]
```

### Integration with Other Barrot Systems
```python
from barrot_integration import barrot_system

# Email analysis integrated with full system
emails = [...]
result = barrot_system.analyze_emails_with_intelligence(emails)

# The result includes:
# - Standard email analysis
# - AGI-powered deep insights
# - Quantum-optimized action prioritization
# - Performance metrics
# - Intelligence summary
```

## Troubleshooting

### Common Issues

**Issue**: Low usefulness scores for important emails
**Solution**: Customize the patterns and keywords to match your specific needs

**Issue**: Spam detection false positives
**Solution**: The spam detector is conservative. Review manually if needed.

**Issue**: Missing action items
**Solution**: Action extraction works best with clear language. Ambiguous requests may not be detected.

## Examples

See `example_email_analysis.py` for comprehensive examples:

```bash
python3 example_email_analysis.py
```

This demonstrates:
1. Single email analysis
2. Batch email processing
3. Learning content extraction
4. Opportunity detection
5. Spam filtering
6. Report export

## Integration with Workflows

### Daily Automation
Add to your daily Barrot workflow:

```yaml
email_intelligence_extraction:
  description: "Analyze emails and extract useful information for Barrot"
  frequency: "daily"
  steps:
    - "Connect to email source"
    - "Fetch unprocessed emails"
    - "Analyze with AGI + Quantum"
    - "Extract actionable insights"
    - "Update knowledge base"
    - "Generate priority report"
```

## API Reference

### `analyze_email(email_data: Dict) -> Dict`
Analyze a single email and return comprehensive analysis.

### `analyze_emails(emails: List[Dict]) -> Dict`
Analyze multiple emails and return batch analysis with summary.

### `process_emails(emails: List[Dict]) -> Dict`
Process emails with full Barrot intelligence (AGI + Quantum).

### `email_analyzer.export_analysis_report(filepath: str)`
Export comprehensive analysis report to JSON file.

## Future Enhancements
- Automatic email source connection
- Smart reply suggestions
- Email template detection
- Conversation threading
- Attachment analysis
- Multi-language support
- Custom ML models for classification

## Support
For issues or questions about email processing, refer to:
- [Email-Insight Spell Documentation](spells/email-insight.md)
- [AI Tools Configuration](ai-tools-config.yaml)
- [Barrot Integration Examples](example_email_analysis.py)

---

**Barrot-Agent Email Intelligence** - Helping Barrot understand and act on email communications efficiently 📧✨
