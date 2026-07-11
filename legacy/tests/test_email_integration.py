"""
Test the full Barrot email intelligence integration
"""

from barrot_integration import process_emails, barrot_system
from datetime import datetime, timezone
import json

def test_email_intelligence():
    """Test email processing with full Barrot intelligence"""
    print("=" * 70)
    print("Testing Barrot Email Intelligence Integration")
    print("=" * 70)
    
    # Sample emails for testing
    test_emails = [
        {
            "id": "test_001",
            "subject": "Urgent: Security vulnerability in production API",
            "sender": "security@company.com",
            "body": """
            Critical security alert!
            
            We've detected a SQL injection vulnerability in the production API.
            Please review the security report and apply the patch immediately.
            Deadline: Today by 5 PM
            
            Security report: https://security.company.com/report/CVE-2024-001
            Patch available at: https://github.com/company/api-security-patch
            
            This requires immediate action.
            """,
            "date": datetime.now(timezone.utc).isoformat(),
            "attachments": ["security_report.pdf"]
        },
        {
            "id": "test_002",
            "subject": "New Machine Learning course - Advanced NLP techniques",
            "sender": "courses@university.edu",
            "body": """
            Exciting new course on Advanced Natural Language Processing!
            
            Learn state-of-the-art NLP techniques including:
            - Transformer architectures
            - BERT and GPT models
            - Fine-tuning best practices
            - Real-world applications
            
            Course materials: https://university.edu/nlp-course
            GitHub repo: https://github.com/university/nlp-examples
            Documentation: https://docs.nlp-course.edu/
            
            Starts next week!
            """,
            "date": datetime.now(timezone.utc).isoformat(),
            "attachments": ["course_outline.pdf"]
        },
        {
            "id": "test_003",
            "subject": "Partnership opportunity - AI collaboration project",
            "sender": "partner@startup.ai",
            "body": """
            Dear Team,
            
            We're looking to collaborate on an exciting AI project with potential
            for significant funding. This partnership could lead to:
            - Joint development of cutting-edge AI tools
            - Revenue sharing agreement
            - Access to our enterprise customer base
            - Co-authoring research papers
            
            We have $2M in seed funding and are looking for technical partners.
            
            Would you be interested in a call to discuss this opportunity?
            """,
            "date": datetime.now(timezone.utc).isoformat(),
            "attachments": ["partnership_proposal.pdf"]
        },
        {
            "id": "test_004",
            "subject": "FREE MONEY! Click here now! Limited time offer!",
            "sender": "noreply@spam-domain.xyz",
            "body": """
            Congratulations! You've won $1,000,000!!!
            
            Click here immediately! Act now! Limited time!
            Free money waiting! Unsubscribe link at bottom.
            
            This is a once in a lifetime opportunity!
            """,
            "date": datetime.now(timezone.utc).isoformat(),
            "attachments": []
        },
        {
            "id": "test_005",
            "subject": "Team standup meeting - Tomorrow at 10 AM",
            "sender": "manager@company.com",
            "body": """
            Hi team,
            
            Reminder: Our weekly standup is tomorrow at 10 AM.
            
            Please come prepared to discuss:
            - Progress on current sprint
            - Any blockers
            - Plans for next week
            
            Meeting link: https://zoom.us/meeting/123456
            """,
            "date": datetime.now(timezone.utc).isoformat(),
            "attachments": []
        }
    ]
    
    # Process emails with full Barrot intelligence
    print("\nProcessing emails with Barrot's integrated intelligence...")
    print("(AGI Reasoning + Quantum Optimization + Email Analysis)\n")
    
    result = process_emails(test_emails)
    
    # Display results
    print("=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    
    print(f"\n📊 Overall Statistics:")
    print(f"  Total Emails Processed: {result['email_analysis']['total_emails']}")
    print(f"  Useful Emails: {result['email_analysis']['useful_emails']}")
    print(f"  High Priority: {result['email_analysis']['high_priority_count']}")
    print(f"  Action Items Found: {result['email_analysis']['total_action_items']}")
    print(f"  Opportunities Found: {result['email_analysis']['total_opportunities']}")
    print(f"  Processing Time: {result['processing_time_seconds']:.3f} seconds")
    
    print(f"\n💡 Intelligence Summary:")
    print(f"  {result['intelligence_summary']}")
    
    if result['agi_insights']:
        print(f"\n🧠 AGI Deep Insights:")
        for i, insight in enumerate(result['agi_insights'], 1):
            print(f"  {i}. Email: {insight['email_subject']}")
            agi = insight['agi_analysis']
            print(f"     Confidence: {agi['reasoning_chain']['overall_confidence']:.2f}")
            print(f"     Reasoning Steps: {len(agi['reasoning_chain']['steps'])}")
    
    print(f"\n⚠️  High Priority Emails:")
    for email in result['email_analysis']['high_priority_emails'][:3]:
        print(f"  • {email['subject']}")
        print(f"    From: {email['sender']}")
        print(f"    Priority: {email['priority'].upper()}")
        print(f"    Recommendation: {email['recommendation']}")
        print()
    
    if result['email_analysis']['opportunities']:
        print(f"🎯 Opportunities Detected:")
        for opp in result['email_analysis']['opportunities']:
            print(f"  • {opp['type'].upper()}: {opp['subject']}")
            print(f"    From: {opp['email_sender']}")
    
    print("\n" + "=" * 70)
    print("✅ Email Intelligence Test Complete!")
    print("=" * 70)
    
    # Export detailed report (excluding non-serializable objects)
    report_file = "/tmp/test_email_intelligence_report.json"
    serializable_result = {
        "email_analysis": result['email_analysis'],
        "processing_time_seconds": result['processing_time_seconds'],
        "intelligence_summary": result['intelligence_summary'],
        "timestamp": result['timestamp'],
        "agi_insights_count": len(result['agi_insights'])
    }
    with open(report_file, 'w') as f:
        json.dump(serializable_result, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    print("\n🎉 Barrot can now analyze emails and extract useful information!")
    print("   - Identifies action items and deadlines")
    print("   - Detects opportunities and learning content")
    print("   - Filters spam and low-value emails")
    print("   - Prioritizes using quantum optimization")
    print("   - Provides AGI-powered insights")
    

if __name__ == "__main__":
    test_email_intelligence()
