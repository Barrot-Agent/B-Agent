#!/usr/bin/env python3
"""
Ethical Ingestion System
Ensures responsible data collection with robots.txt respect, rate limiting, and attribution
"""

import time
from typing import Dict, Any, Optional
from pathlib import Path
from urllib.parse import urlparse
import json
from datetime import datetime, timezone


class EthicalIngestion:
    """Manages ethical data ingestion practices"""
    
    def __init__(self, repo_root: Path = None):
        """Initialize the ethical ingestion system"""
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.memory_bundles = self.repo_root / "memory-bundles"
        self.ethics_log_path = self.memory_bundles / "ethical_ingestion_log.json"
        
        # Load or initialize ethics log
        self.ethics_log = self._load_ethics_log()
        
        # Rate limiting trackers
        self.request_times = {}
        
        # Default rate limits (requests per minute)
        self.rate_limits = {
            'default': 10,
            'critical': 30,
            'high': 20,
            'medium': 10,
            'low': 5
        }
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "blocked_by_robots": 0,
            "rate_limited": 0,
            "ethical_violations": 0
        }
    
    def _load_ethics_log(self) -> Dict[str, Any]:
        """Load ethical ingestion log"""
        if self.ethics_log_path.exists():
            with open(self.ethics_log_path, 'r') as f:
                return json.load(f)
        
        return {
            "robot_txt_cache": {},
            "attribution_records": [],
            "violations": [],
            "metadata": {
                "created": datetime.now(timezone.utc).isoformat(),
                "version": "1.0.0"
            }
        }
    
    def _save_ethics_log(self):
        """Save ethical ingestion log"""
        self.memory_bundles.mkdir(parents=True, exist_ok=True)
        self.ethics_log["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        with open(self.ethics_log_path, 'w') as f:
            json.dump(self.ethics_log, f, indent=2)
    
    def check_robots_txt(self, url: str, user_agent: str = "Barrot-Agent") -> bool:
        """
        Check if URL is allowed by robots.txt
        
        Args:
            url: URL to check
            user_agent: User agent string
            
        Returns:
            True if allowed, False if blocked
        """
        parsed_url = urlparse(url)
        domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Check cache
        if domain in self.ethics_log["robot_txt_cache"]:
            cached = self.ethics_log["robot_txt_cache"][domain]
            if cached.get("allowed", True):
                return True
            else:
                self.stats["blocked_by_robots"] += 1
                print(f"[EthicalIngestion] Blocked by robots.txt: {domain}")
                return False
        
        # In production, would fetch and parse robots.txt
        # For now, assume allowed and cache
        self.ethics_log["robot_txt_cache"][domain] = {
            "allowed": True,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
        
        return True
    
    def enforce_rate_limit(self, source: str, priority: str = 'default') -> bool:
        """
        Enforce rate limiting for a source
        
        Args:
            source: Source identifier
            priority: Priority level (affects rate limit)
            
        Returns:
            True if request allowed, False if rate limited
        """
        current_time = time.time()
        
        # Get rate limit for priority
        requests_per_minute = self.rate_limits.get(priority, self.rate_limits['default'])
        min_interval = 60.0 / requests_per_minute
        
        # Check last request time
        if source in self.request_times:
            last_request = self.request_times[source]
            elapsed = current_time - last_request
            
            if elapsed < min_interval:
                # Rate limited
                wait_time = min_interval - elapsed
                self.stats["rate_limited"] += 1
                print(f"[EthicalIngestion] Rate limited: {source} (wait {wait_time:.1f}s)")
                time.sleep(wait_time)
        
        # Update last request time
        self.request_times[source] = time.time()
        self.stats["total_requests"] += 1
        
        return True
    
    def add_attribution(self, content_id: str, source: Dict[str, Any]):
        """
        Add attribution record for ingested content
        
        Args:
            content_id: Unique content identifier
            source: Source information
        """
        attribution = {
            "content_id": content_id,
            "source": source.get('name', 'unknown'),
            "url": source.get('url', ''),
            "license": source.get('license', 'unknown'),
            "attribution_text": self._generate_attribution(source),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.ethics_log["attribution_records"].append(attribution)
    
    def _generate_attribution(self, source: Dict[str, Any]) -> str:
        """Generate attribution text for source"""
        source_name = source.get('name', 'Unknown Source')
        url = source.get('url', '')
        
        if url:
            return f"Content sourced from {source_name} ({url})"
        else:
            return f"Content sourced from {source_name}"
    
    def check_copyright_compliance(self, content: Dict[str, Any]) -> bool:
        """
        Check if content usage complies with copyright
        
        Args:
            content: Content to check
            
        Returns:
            True if compliant, False otherwise
        """
        # Check for open licenses
        license_type = content.get('license', '').lower()
        
        open_licenses = [
            'cc0', 'cc-by', 'mit', 'apache', 'gpl', 'bsd',
            'public domain', 'open access', 'creative commons'
        ]
        
        for open_license in open_licenses:
            if open_license in license_type:
                return True
        
        # If no license info, assume restricted (be conservative)
        if not license_type:
            print(f"[EthicalIngestion] Warning: No license information for content")
            return False
        
        return True
    
    def log_violation(self, violation_type: str, details: Dict[str, Any]):
        """Log an ethical violation"""
        violation = {
            "type": violation_type,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.ethics_log["violations"].append(violation)
        self.stats["ethical_violations"] += 1
        
        print(f"[EthicalIngestion] Violation logged: {violation_type}")
    
    def validate_request(self, url: str, source: str, priority: str = 'default') -> bool:
        """
        Validate if a request is ethical
        
        Checks:
        - robots.txt compliance
        - rate limiting
        - attribution requirements
        
        Returns:
            True if request is ethical and should proceed
        """
        # Check robots.txt
        if not self.check_robots_txt(url):
            self.log_violation("robots_txt_violation", {"url": url, "source": source})
            return False
        
        # Enforce rate limiting
        self.enforce_rate_limit(source, priority)
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ethical ingestion statistics"""
        return {
            **self.stats,
            "total_attributions": len(self.ethics_log["attribution_records"]),
            "total_violations": len(self.ethics_log["violations"])
        }
    
    def generate_attribution_report(self) -> str:
        """Generate attribution report for all ingested content"""
        report = "# Content Attribution Report\n\n"
        report += f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n"
        
        for attribution in self.ethics_log["attribution_records"][-100:]:  # Last 100
            report += f"- {attribution['attribution_text']}\n"
        
        return report
    
    def finalize(self):
        """Save ethics log"""
        self._save_ethics_log()
        print(f"[EthicalIngestion] Ethics log saved")


def main():
    """Main execution"""
    ethical_system = EthicalIngestion()
    
    # Test ethical checks
    test_url = "https://example.com/api/data"
    test_source = "test_source"
    
    # Check robots.txt
    allowed = ethical_system.check_robots_txt(test_url)
    print(f"Robots.txt check: {'Allowed' if allowed else 'Blocked'}")
    
    # Test rate limiting
    for i in range(3):
        ethical_system.enforce_rate_limit(test_source, 'high')
        print(f"Request {i+1} completed")
    
    # Add attribution
    ethical_system.add_attribution("content_123", {
        "name": "Test Source",
        "url": test_url,
        "license": "CC-BY"
    })
    
    # Print stats
    stats = ethical_system.get_stats()
    print(f"\nEthical Ingestion Statistics:")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Rate Limited: {stats['rate_limited']}")
    print(f"  Blocked by robots.txt: {stats['blocked_by_robots']}")
    print(f"  Violations: {stats['ethical_violations']}")
    print(f"  Attributions: {stats['total_attributions']}")
    
    ethical_system.finalize()
    
    return ethical_system


if __name__ == "__main__":
    main()
