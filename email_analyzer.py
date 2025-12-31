"""
Email Analyzer for Barrot-Agent
Analyzes emails and extracts useful, actionable information
"""

import json
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from enum import Enum


class EmailPriority(Enum):
    """Email priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NOISE = "noise"


class EmailCategory(Enum):
    """Email categories"""
    ACTION_REQUIRED = "action_required"
    LEARNING_OPPORTUNITY = "learning_opportunity"
    BUSINESS_OPPORTUNITY = "business_opportunity"
    INTELLIGENCE = "intelligence"
    SOCIAL = "social"
    INFORMATIONAL = "informational"
    NOTIFICATION = "notification"
    SPAM = "spam"


class EmailAnalyzer:
    """
    Analyzes emails to determine usefulness and extract actionable information
    """
    
    def __init__(self):
        self.analysis_history = []
        self.knowledge_patterns = self._initialize_knowledge_patterns()
        self.action_patterns = self._initialize_action_patterns()
        self.opportunity_keywords = self._initialize_opportunity_keywords()
        
    def _initialize_knowledge_patterns(self) -> List[str]:
        """Initialize patterns that indicate learning opportunities"""
        return [
            r'\b(tutorial|guide|how[-\s]to|learn|course|documentation|docs)\b',
            r'\b(API|library|framework|tool|platform|service)\b',
            r'\b(research|paper|study|analysis|report)\b',
            r'\b(algorithm|implementation|code|example)\b',
            r'\b(best[-\s]practice|pattern|architecture)\b',
        ]
    
    def _initialize_action_patterns(self) -> List[str]:
        """Initialize patterns that indicate action items"""
        return [
            r'\b(please|kindly|could\s+you|would\s+you|need\s+you\s+to)\b',
            r'\b(deadline|due\s+date|by\s+\d+|urgent|asap|priority)\b',
            r'\b(action\s+required|respond|reply|confirm|approve)\b',
            r'\b(meeting|call|schedule|appointment)\b',
            r'\b(complete|finish|submit|deliver|provide)\b',
        ]
    
    def _initialize_opportunity_keywords(self) -> Dict[str, List[str]]:
        """Initialize keywords for different opportunity types"""
        return {
            "job": ["job", "position", "opportunity", "hiring", "career", "role", "opening"],
            "collaboration": ["collaborate", "partnership", "joint", "together", "team up"],
            "business": ["contract", "proposal", "deal", "investment", "funding", "revenue"],
            "speaking": ["speak", "present", "talk", "conference", "event", "keynote"],
            "consulting": ["consult", "advisory", "expert", "specialist", "freelance"],
        }
    
    def analyze_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single email and extract useful information
        
        Args:
            email_data: Dictionary containing email information
                - subject: Email subject line
                - sender: Email sender address
                - body: Email body content
                - date: Email date
                - attachments: List of attachments (optional)
        
        Returns:
            Analysis results with priority, categories, and extracted information
        """
        subject = email_data.get("subject", "")
        sender = email_data.get("sender", "")
        body = email_data.get("body", "")
        date = email_data.get("date", datetime.now(timezone.utc).isoformat())
        attachments = email_data.get("attachments", [])
        
        # Combine subject and body for analysis
        full_content = f"{subject} {body}".lower()
        
        # Determine priority
        priority = self._calculate_priority(full_content, sender, attachments)
        
        # Categorize email
        categories = self._categorize_email(full_content, sender)
        
        # Extract actionable items
        action_items = self._extract_action_items(subject, body)
        
        # Extract learning opportunities
        learning_content = self._extract_learning_content(full_content, attachments)
        
        # Extract opportunities
        opportunities = self._extract_opportunities(full_content, subject)
        
        # Extract resources and links
        resources = self._extract_resources(body)
        
        # Calculate usefulness score
        usefulness_score = self._calculate_usefulness_score(
            priority, categories, action_items, learning_content, opportunities
        )
        
        # Determine if email is useful to Barrot
        is_useful = usefulness_score >= 0.3
        
        analysis = {
            "email_id": email_data.get("id", f"email_{hash(subject)}"),
            "subject": subject,
            "sender": sender,
            "date": date,
            "priority": priority.value,
            "categories": [cat.value for cat in categories],
            "usefulness_score": round(usefulness_score, 2),
            "is_useful": is_useful,
            "action_items": action_items,
            "learning_content": learning_content,
            "opportunities": opportunities,
            "resources": resources,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "recommendation": self._generate_recommendation(
                is_useful, priority, categories, action_items, opportunities
            )
        }
        
        # Store in history
        self.analysis_history.append(analysis)
        
        return analysis
    
    def _calculate_priority(self, content: str, sender: str, attachments: List[str]) -> EmailPriority:
        """Calculate email priority based on content and context"""
        priority_score = 0
        
        # Check for urgency indicators
        urgency_keywords = ["urgent", "asap", "immediately", "critical", "priority", "emergency"]
        for keyword in urgency_keywords:
            if keyword in content:
                priority_score += 3
        
        # Check for deadline mentions
        if re.search(r'\b(deadline|due\s+date|by\s+\d+)\b', content):
            priority_score += 2
        
        # Check for action patterns
        for pattern in self.action_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                priority_score += 1
        
        # Attachments may indicate important content
        if attachments:
            priority_score += 1
        
        # Classify based on score
        if priority_score >= 5:
            return EmailPriority.HIGH
        elif priority_score >= 2:
            return EmailPriority.MEDIUM
        elif priority_score >= 1:
            return EmailPriority.LOW
        else:
            return EmailPriority.NOISE
    
    def _categorize_email(self, content: str, sender: str) -> List[EmailCategory]:
        """Categorize email into one or more categories"""
        categories = []
        
        # Check for spam indicators
        spam_keywords = ["unsubscribe", "click here", "limited time", "act now", "free money"]
        if sum(1 for keyword in spam_keywords if keyword in content) >= 2:
            categories.append(EmailCategory.SPAM)
            return categories  # If spam, return early
        
        # Check for action items
        for pattern in self.action_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                categories.append(EmailCategory.ACTION_REQUIRED)
                break
        
        # Check for learning opportunities
        for pattern in self.knowledge_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                categories.append(EmailCategory.LEARNING_OPPORTUNITY)
                break
        
        # Check for business opportunities
        for opp_type, keywords in self.opportunity_keywords.items():
            if any(keyword in content for keyword in keywords):
                categories.append(EmailCategory.BUSINESS_OPPORTUNITY)
                break
        
        # Check for intelligence/insights
        intel_keywords = ["trend", "market", "industry", "competitor", "analysis", "insight"]
        if any(keyword in content for keyword in intel_keywords):
            categories.append(EmailCategory.INTELLIGENCE)
        
        # Check for social content
        social_keywords = ["thank you", "thanks", "appreciate", "congratulations", "welcome"]
        if any(keyword in content for keyword in social_keywords):
            categories.append(EmailCategory.SOCIAL)
        
        # Default to informational or notification
        if not categories:
            if "notification" in content or re.search(r'\bno[-\s]?reply\b', sender):
                categories.append(EmailCategory.NOTIFICATION)
            else:
                categories.append(EmailCategory.INFORMATIONAL)
        
        return categories
    
    def _extract_action_items(self, subject: str, body: str) -> List[Dict[str, str]]:
        """Extract action items from email"""
        action_items = []
        
        # Look for explicit action requests
        action_sentences = []
        for pattern in self.action_patterns:
            matches = re.finditer(pattern, body, re.IGNORECASE)
            for match in matches:
                # Get the sentence containing the match
                start = max(0, body.rfind('.', 0, match.start()) + 1)
                end = body.find('.', match.end())
                if end == -1:
                    end = len(body)
                sentence = body[start:end].strip()
                if sentence and len(sentence) > 10:
                    action_sentences.append(sentence)
        
        # Remove duplicates and create action items
        seen = set()
        for sentence in action_sentences:
            sentence_lower = sentence.lower()
            if sentence_lower not in seen:
                seen.add(sentence_lower)
                action_items.append({
                    "description": sentence[:200],  # Limit length
                    "context": "extracted from email body"
                })
        
        return action_items[:5]  # Limit to top 5 action items
    
    def _extract_learning_content(self, content: str, attachments: List[str]) -> List[Dict[str, str]]:
        """Extract learning opportunities from email"""
        learning_items = []
        
        # Check for technical content
        for pattern in self.knowledge_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                learning_items.append({
                    "type": "technical_content",
                    "source": "email_body",
                    "relevance": "high"
                })
                break
        
        # Check for educational attachments
        educational_extensions = ['.pdf', '.doc', '.ppt', '.md', '.txt']
        for attachment in attachments:
            if any(attachment.lower().endswith(ext) for ext in educational_extensions):
                learning_items.append({
                    "type": "educational_document",
                    "source": attachment,
                    "relevance": "medium"
                })
        
        return learning_items
    
    def _extract_opportunities(self, content: str, subject: str) -> List[Dict[str, str]]:
        """Extract opportunities from email"""
        opportunities = []
        
        for opp_type, keywords in self.opportunity_keywords.items():
            if any(keyword in content for keyword in keywords):
                opportunities.append({
                    "type": opp_type,
                    "subject": subject[:100],
                    "potential": "medium"  # Could be enhanced with more sophisticated analysis
                })
        
        return opportunities
    
    def _extract_resources(self, body: str) -> List[Dict[str, str]]:
        """Extract URLs and resource links from email"""
        resources = []
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, body)
        
        for url in urls[:10]:  # Limit to 10 URLs
            # Categorize URL
            url_type = "general"
            if "github.com" in url:
                url_type = "code_repository"
            elif any(domain in url for domain in ["docs.", "documentation", "/docs/"]):
                url_type = "documentation"
            elif any(domain in url for domain in ["youtube.com", "vimeo.com"]):
                url_type = "video"
            elif any(domain in url for domain in ["arxiv.org", "scholar.google"]):
                url_type = "research"
            
            resources.append({
                "url": url,
                "type": url_type
            })
        
        return resources
    
    def _calculate_usefulness_score(
        self,
        priority: EmailPriority,
        categories: List[EmailCategory],
        action_items: List[Dict[str, str]],
        learning_content: List[Dict[str, str]],
        opportunities: List[Dict[str, str]]
    ) -> float:
        """Calculate overall usefulness score (0.0 to 1.0)"""
        score = 0.0
        
        # Priority contribution
        priority_weights = {
            EmailPriority.HIGH: 0.3,
            EmailPriority.MEDIUM: 0.2,
            EmailPriority.LOW: 0.1,
            EmailPriority.NOISE: 0.0
        }
        score += priority_weights.get(priority, 0.0)
        
        # Category contribution
        useful_categories = [
            EmailCategory.ACTION_REQUIRED,
            EmailCategory.LEARNING_OPPORTUNITY,
            EmailCategory.BUSINESS_OPPORTUNITY,
            EmailCategory.INTELLIGENCE
        ]
        for category in categories:
            if category in useful_categories:
                score += 0.15
            elif category == EmailCategory.SPAM:
                return 0.0  # Spam is not useful
        
        # Action items contribution
        if action_items:
            score += min(len(action_items) * 0.1, 0.2)
        
        # Learning content contribution
        if learning_content:
            score += min(len(learning_content) * 0.1, 0.2)
        
        # Opportunities contribution
        if opportunities:
            score += min(len(opportunities) * 0.15, 0.3)
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _generate_recommendation(
        self,
        is_useful: bool,
        priority: EmailPriority,
        categories: List[EmailCategory],
        action_items: List[Dict[str, str]],
        opportunities: List[Dict[str, str]]
    ) -> str:
        """Generate recommendation for handling the email"""
        if not is_useful:
            return "Archive or delete - low value content"
        
        if EmailCategory.ACTION_REQUIRED in categories:
            return f"Action required - {len(action_items)} item(s) need attention"
        
        if opportunities:
            return f"Review opportunities - {len(opportunities)} potential opportunity(ies)"
        
        if EmailCategory.LEARNING_OPPORTUNITY in categories:
            return "Review for learning - contains useful technical content"
        
        if priority == EmailPriority.HIGH:
            return "High priority - review and respond promptly"
        
        return "Review when convenient - informational content"
    
    def analyze_batch(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze multiple emails and provide summary insights
        
        Args:
            emails: List of email data dictionaries
        
        Returns:
            Batch analysis results with summaries and priorities
        """
        analyses = [self.analyze_email(email) for email in emails]
        
        # Categorize by usefulness
        useful_emails = [a for a in analyses if a["is_useful"]]
        not_useful_emails = [a for a in analyses if not a["is_useful"]]
        
        # Categorize by priority
        high_priority = [a for a in analyses if a["priority"] == EmailPriority.HIGH.value]
        medium_priority = [a for a in analyses if a["priority"] == EmailPriority.MEDIUM.value]
        
        # Extract all action items
        all_action_items = []
        for analysis in analyses:
            for item in analysis["action_items"]:
                all_action_items.append({
                    **item,
                    "email_subject": analysis["subject"],
                    "email_sender": analysis["sender"]
                })
        
        # Extract all opportunities
        all_opportunities = []
        for analysis in analyses:
            for opp in analysis["opportunities"]:
                all_opportunities.append({
                    **opp,
                    "email_subject": analysis["subject"],
                    "email_sender": analysis["sender"]
                })
        
        return {
            "total_emails": len(emails),
            "useful_emails": len(useful_emails),
            "not_useful_emails": len(not_useful_emails),
            "high_priority_count": len(high_priority),
            "medium_priority_count": len(medium_priority),
            "total_action_items": len(all_action_items),
            "total_opportunities": len(all_opportunities),
            "high_priority_emails": high_priority[:5],  # Top 5
            "action_items": all_action_items[:10],  # Top 10
            "opportunities": all_opportunities[:5],  # Top 5
            "detailed_analyses": analyses,
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": self._generate_batch_summary(
                len(emails), len(useful_emails), len(high_priority), 
                len(all_action_items), len(all_opportunities)
            )
        }
    
    def _generate_batch_summary(
        self, 
        total: int, 
        useful: int, 
        high_priority: int,
        action_items: int, 
        opportunities: int
    ) -> str:
        """Generate human-readable summary of batch analysis"""
        useful_pct = (useful / total * 100) if total > 0 else 0
        
        summary = f"Analyzed {total} emails: "
        summary += f"{useful} ({useful_pct:.0f}%) are useful to Barrot. "
        
        if high_priority > 0:
            summary += f"{high_priority} require immediate attention. "
        
        if action_items > 0:
            summary += f"Found {action_items} action items. "
        
        if opportunities > 0:
            summary += f"Identified {opportunities} opportunities. "
        
        if useful_pct < 20:
            summary += "Consider updating email filters to reduce noise."
        elif useful_pct > 80:
            summary += "High signal-to-noise ratio - email sources are well-curated."
        
        return summary.strip()
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get all email analysis history"""
        return self.analysis_history
    
    def export_analysis_report(self, filepath: str = "email_analysis_report.json"):
        """Export comprehensive analysis report"""
        report = {
            "email_analyzer_report": {
                "version": "1.0.0",
                "total_emails_analyzed": len(self.analysis_history),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "analysis_history": self.analysis_history
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


# Global email analyzer instance
email_analyzer = EmailAnalyzer()


def analyze_email(email_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenient function to analyze a single email
    
    Args:
        email_data: Email information dictionary
    
    Returns:
        Analysis results
    """
    return email_analyzer.analyze_email(email_data)


def analyze_emails(emails: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convenient function to analyze multiple emails
    
    Args:
        emails: List of email information dictionaries
    
    Returns:
        Batch analysis results
    """
    return email_analyzer.analyze_batch(emails)
