"""
Example usage of Email Analyzer for Barrot-Agent
Demonstrates how to analyze emails and extract useful information
"""

from email_analyzer import analyze_email, analyze_emails, email_analyzer
from datetime import datetime, timezone
import json


def example_single_email_analysis():
    """Demonstrate analysis of a single email"""
    print("=" * 70)
    print("Example 1: Single Email Analysis")
    print("=" * 70)
    
    # Example email with technical content and action items
    email = {
        "id": "email_001",
        "subject": "New Python library for machine learning - Review needed by Friday",
        "sender": "colleague@company.com",
        "body": """
        Hi,
        
        I found this interesting new Python library for machine learning called FastML.
        It has great documentation at https://fastml.readthedocs.io/ and the GitHub 
        repository is at https://github.com/fastml/fastml.
        
        Could you please review the API and give me your feedback by Friday? 
        We need to decide if we should integrate this into our project.
        
        The library offers:
        - Fast model training
        - Easy deployment
        - Great community support
        
        Let me know what you think!
        
        Best regards
        """,
        "date": datetime.now(timezone.utc).isoformat(),
        "attachments": ["fastml_comparison.pdf"]
    }
    
    result = analyze_email(email)
    
    print(f"Subject: {result['subject']}")
    print(f"Sender: {result['sender']}")
    print(f"Priority: {result['priority']}")
    print(f"Usefulness Score: {result['usefulness_score']}")
    print(f"Is Useful: {result['is_useful']}")
    print(f"Categories: {', '.join(result['categories'])}")
    print(f"\nRecommendation: {result['recommendation']}")
    
    if result['action_items']:
        print(f"\nAction Items ({len(result['action_items'])}):")
        for i, item in enumerate(result['action_items'], 1):
            print(f"  {i}. {item['description']}")
    
    if result['resources']:
        print(f"\nResources Found ({len(result['resources'])}):")
        for resource in result['resources']:
            print(f"  - {resource['type']}: {resource['url']}")
    
    print()


def example_batch_email_analysis():
    """Demonstrate analysis of multiple emails"""
    print("=" * 70)
    print("Example 2: Batch Email Analysis")
    print("=" * 70)
    
    emails = [
        {
            "id": "email_001",
            "subject": "Urgent: Server maintenance required",
            "sender": "ops@company.com",
            "body": "The production server needs immediate attention. Please respond ASAP.",
            "date": datetime.now(timezone.utc).isoformat(),
            "attachments": []
        },
        {
            "id": "email_002",
            "subject": "Weekly newsletter - Tech trends",
            "sender": "newsletter@techblog.com",
            "body": "Check out the latest trends in AI and machine learning...",
            "date": datetime.now(timezone.utc).isoformat(),
            "attachments": []
        },
        {
            "id": "email_003",
            "subject": "Job opportunity - Senior Engineer position",
            "sender": "recruiter@bigtech.com",
            "body": "We have an exciting opportunity for a Senior Engineer role. Great benefits and competitive salary.",
            "date": datetime.now(timezone.utc).isoformat(),
            "attachments": []
        },
        {
            "id": "email_004",
            "subject": "Limited time offer - Click now!",
            "sender": "marketing@spam.com",
            "body": "Act now! Free money! Click here! Unsubscribe at bottom.",
            "date": datetime.now(timezone.utc).isoformat(),
            "attachments": []
        },
        {
            "id": "email_005",
            "subject": "Tutorial: Advanced Python techniques",
            "sender": "education@learning.com",
            "body": "Learn advanced Python patterns and best practices. Full tutorial at https://learning.com/python",
            "date": datetime.now(timezone.utc).isoformat(),
            "attachments": ["python_tutorial.pdf"]
        }
    ]
    
    result = analyze_emails(emails)
    
    print(f"Total Emails: {result['total_emails']}")
    print(f"Useful Emails: {result['useful_emails']}")
    print(f"Not Useful: {result['not_useful_emails']}")
    print(f"High Priority: {result['high_priority_count']}")
    print(f"Medium Priority: {result['medium_priority_count']}")
    print(f"Total Action Items: {result['total_action_items']}")
    print(f"Total Opportunities: {result['total_opportunities']}")
    
    print(f"\nSummary: {result['summary']}")
    
    if result['high_priority_emails']:
        print(f"\nHigh Priority Emails:")
        for email in result['high_priority_emails']:
            print(f"  - {email['subject']} (from {email['sender']})")
    
    if result['opportunities']:
        print(f"\nOpportunities Found:")
        for opp in result['opportunities']:
            print(f"  - {opp['type']}: {opp['subject']}")
    
    print()


def example_learning_content_extraction():
    """Demonstrate extraction of learning content"""
    print("=" * 70)
    print("Example 3: Learning Content Extraction")
    print("=" * 70)
    
    email = {
        "id": "email_learning",
        "subject": "New course on Quantum Computing",
        "sender": "courses@university.edu",
        "body": """
        Exciting new course alert!
        
        Learn quantum computing fundamentals in this comprehensive tutorial.
        Topics covered:
        - Quantum algorithms
        - Quantum entanglement
        - Implementation examples
        
        Course materials: https://university.edu/quantum-course
        Research paper: https://arxiv.org/quantum-computing-intro
        Code examples: https://github.com/university/quantum-examples
        
        Documentation available at https://docs.quantum.edu/
        """,
        "date": datetime.now(timezone.utc).isoformat(),
        "attachments": ["quantum_syllabus.pdf", "lecture_notes.pdf"]
    }
    
    result = analyze_email(email)
    
    print(f"Subject: {result['subject']}")
    print(f"Categories: {', '.join(result['categories'])}")
    
    if result['learning_content']:
        print(f"\nLearning Content ({len(result['learning_content'])} items):")
        for content in result['learning_content']:
            print(f"  - Type: {content['type']}")
            print(f"    Source: {content['source']}")
            print(f"    Relevance: {content['relevance']}")
    
    if result['resources']:
        print(f"\nEducational Resources:")
        for resource in result['resources']:
            print(f"  - {resource['type']}: {resource['url']}")
    
    print()


def example_opportunity_detection():
    """Demonstrate opportunity detection"""
    print("=" * 70)
    print("Example 4: Opportunity Detection")
    print("=" * 70)
    
    email = {
        "id": "email_opportunity",
        "subject": "Partnership proposal for AI collaboration",
        "sender": "partner@startup.com",
        "body": """
        Dear Team,
        
        We're looking for a partnership to collaborate on an exciting AI project.
        This is a great opportunity to work together on cutting-edge technology.
        
        We're offering:
        - Joint development
        - Revenue sharing
        - Access to our platform
        
        We have funding secured and are looking for the right team to partner with.
        
        Would you be interested in discussing this opportunity further?
        """,
        "date": datetime.now(timezone.utc).isoformat(),
        "attachments": ["partnership_proposal.pdf"]
    }
    
    result = analyze_email(email)
    
    print(f"Subject: {result['subject']}")
    print(f"Priority: {result['priority']}")
    print(f"Usefulness Score: {result['usefulness_score']}")
    
    if result['opportunities']:
        print(f"\nOpportunities Detected ({len(result['opportunities'])}):")
        for opp in result['opportunities']:
            print(f"  - Type: {opp['type']}")
            print(f"    Subject: {opp['subject']}")
            print(f"    Potential: {opp['potential']}")
    
    print(f"\nRecommendation: {result['recommendation']}")
    print()


def example_spam_detection():
    """Demonstrate spam detection"""
    print("=" * 70)
    print("Example 5: Spam Detection")
    print("=" * 70)
    
    emails = [
        {
            "id": "spam_001",
            "subject": "You won a million dollars! Click here now!",
            "sender": "noreply@spam.com",
            "body": "Congratulations! You won! Click here! Act now! Limited time! Free money! Unsubscribe.",
            "date": datetime.now(timezone.utc).isoformat(),
            "attachments": []
        },
        {
            "id": "legit_001",
            "subject": "Team meeting tomorrow at 2pm",
            "sender": "manager@company.com",
            "body": "Hi team, let's meet tomorrow at 2pm to discuss the project status. Please confirm attendance.",
            "date": datetime.now(timezone.utc).isoformat(),
            "attachments": []
        }
    ]
    
    for email in emails:
        result = analyze_email(email)
        is_spam = 'spam' in result['categories']
        
        print(f"Subject: {result['subject']}")
        print(f"Categories: {', '.join(result['categories'])}")
        print(f"Is Spam: {is_spam}")
        print(f"Usefulness Score: {result['usefulness_score']}")
        print()


def example_export_analysis_report():
    """Demonstrate exporting analysis report"""
    print("=" * 70)
    print("Example 6: Export Analysis Report")
    print("=" * 70)
    
    # Analyze some emails first
    emails = [
        {
            "subject": "Test email 1",
            "sender": "test1@example.com",
            "body": "This is a test email with some content.",
            "date": datetime.now(timezone.utc).isoformat()
        },
        {
            "subject": "Test email 2 - Urgent action needed",
            "sender": "test2@example.com",
            "body": "Please respond to this urgent request by tomorrow.",
            "date": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    analyze_emails(emails)
    
    # Export report
    report = email_analyzer.export_analysis_report("email_analysis_report.json")
    
    print(f"Analysis report exported!")
    print(f"Total emails analyzed: {report['email_analyzer_report']['total_emails_analyzed']}")
    print(f"Report file: email_analysis_report.json")
    print()


def run_all_examples():
    """Run all demonstration examples"""
    print("\n")
    print("*" * 70)
    print("Email Analyzer for Barrot-Agent - Demonstration")
    print("*" * 70)
    print("\n")
    
    example_single_email_analysis()
    example_batch_email_analysis()
    example_learning_content_extraction()
    example_opportunity_detection()
    example_spam_detection()
    example_export_analysis_report()
    
    print("*" * 70)
    print("All Examples Complete!")
    print("*" * 70)
    print("\nThe Email Analyzer can now be integrated into Barrot's workflow")
    print("to automatically process and extract useful information from emails.")
    print()


if __name__ == "__main__":
    run_all_examples()
