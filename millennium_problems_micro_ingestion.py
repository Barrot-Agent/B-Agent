#!/usr/bin/env python3
"""
Millennium Problems Micro-Ingestion System

Extracts and structures all components of MILLENNIUM_PROBLEMS_STATUS.md into:
- JSON formatted data structures
- Search-ready summaries
- Taxonomies and classifications
- Structured knowledge framework

Designed for Barrot.Agent's knowledge base enhancement.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ProblemOverview:
    """Overview table entry for a Millennium Problem"""
    name: str
    prize: str
    status: str
    ai_applicability: str
    progress: str


@dataclass
class ProblemDetails:
    """Detailed information about a specific Millennium Problem"""
    number: int
    name: str
    problem_statement: str
    official_status: str
    barrot_analysis_stage: str
    ai_ml_relevance: str
    why_matters_for_ai: List[str]
    barrot_approach: List[str]
    current_insights: List[str]
    next_steps: List[str]
    progress_status: str


@dataclass
class ExecutiveSummary:
    """Executive summary of the Millennium Problems progress"""
    last_updated: str
    status: str
    purpose: str
    current_stage: str
    problems_solved: str
    problems_under_analysis: str
    ai_ml_applications: str


@dataclass
class ProgressMetrics:
    """Quantitative progress metrics"""
    problems_studied: str
    frameworks_ingested: str
    deep_analysis_started: str
    computational_experiments: str
    publications_reviewed: int
    novel_insights_generated: int
    ai_applications_identified: int


@dataclass
class StrategicPriority:
    """Strategic priority classification"""
    priority_level: str
    problems: List[str]
    description: str


class MillenniumProblemsMicroIngestion:
    """Micro-ingestion system for Millennium Problems document"""
    
    def __init__(self, input_file: str = "MILLENNIUM_PROBLEMS_STATUS.md"):
        self.input_file = input_file
        self.content = ""
        self.problems_overview: List[ProblemOverview] = []
        self.problem_details: List[ProblemDetails] = []
        self.executive_summary: Optional[ExecutiveSummary] = None
        self.progress_metrics: Optional[ProgressMetrics] = None
        self.strategic_priorities: List[StrategicPriority] = []
        self.activity_log: List[Dict[str, str]] = []
        
    def load_document(self) -> bool:
        """Load the Millennium Problems document"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return True
        except FileNotFoundError:
            print(f"Error: File {self.input_file} not found")
            return False
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def extract_executive_summary(self) -> ExecutiveSummary:
        """Extract executive summary information"""
        # Extract metadata from header
        last_updated_match = re.search(r'\*\*Last Updated\*\*:\s*(.+)', self.content)
        status_match = re.search(r'\*\*Status\*\*:\s*(.+)', self.content)
        purpose_match = re.search(r'\*\*Purpose\*\*:\s*(.+)', self.content)
        
        # Extract from Executive Summary section
        exec_section = re.search(
            r'## Executive Summary\s+(.+?)(?=\n##|\Z)', 
            self.content, 
            re.DOTALL
        )
        
        if exec_section:
            exec_text = exec_section.group(1)
            current_stage = re.search(r'\*\*Current Stage\*\*:\s*(.+)', exec_text)
            problems_solved = re.search(r'\*\*Problems Solved\*\*:\s*(.+)', exec_text)
            problems_analysis = re.search(r'\*\*Problems Under Active Analysis\*\*:\s*(.+)', exec_text)
            ai_apps = re.search(r'\*\*AI/ML Applications Identified\*\*:\s*(.+)', exec_text)
        else:
            current_stage = problems_solved = problems_analysis = ai_apps = None
        
        return ExecutiveSummary(
            last_updated=last_updated_match.group(1).strip() if last_updated_match else "",
            status=status_match.group(1).strip() if status_match else "",
            purpose=purpose_match.group(1).strip() if purpose_match else "",
            current_stage=current_stage.group(1).strip() if current_stage else "",
            problems_solved=problems_solved.group(1).strip() if problems_solved else "",
            problems_under_analysis=problems_analysis.group(1).strip() if problems_analysis else "",
            ai_ml_applications=ai_apps.group(1).strip() if ai_apps else ""
        )
    
    def extract_problems_overview_table(self) -> List[ProblemOverview]:
        """Extract the problems overview table and convert to structured format"""
        table_section = re.search(
            r'\| Problem \| Clay Prize \| Status \| AI Applicability \| Progress \|(.+?)(?=\n##|\n\n---)',
            self.content,
            re.DOTALL
        )
        
        if not table_section:
            return []
        
        problems = []
        lines = table_section.group(1).strip().split('\n')
        
        for line in lines:
            # Skip separator lines
            if '---' in line:
                continue
            
            # Parse table row
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 5:
                problems.append(ProblemOverview(
                    name=parts[0],
                    prize=parts[1],
                    status=parts[2],
                    ai_applicability=parts[3],
                    progress=parts[4]
                ))
        
        return problems
    
    def extract_problem_details(self) -> List[ProblemDetails]:
        """Extract detailed information for each problem"""
        problems = []
        
        # Find all problem sections (numbered 1-7)
        # Pattern: ## <number>. <name>\n\n### Problem Statement\n<content>
        # Matches until next ## section or end of document
        problem_sections = re.finditer(
            r'## (\d+)\.\s+(.+?)\n\n### Problem Statement\n(.+?)(?=\n## |\Z)',
            self.content,
            re.DOTALL
        )
        
        for match in problem_sections:
            number = int(match.group(1))
            name = match.group(2).strip()
            full_section = match.group(3)
            
            # Extract problem statement (text before next ### heading)
            # Handle cases where problem statement may extend to end of section
            stmt_match = re.search(r'^(.+?)(?=\n### |\Z)', full_section, re.DOTALL)
            problem_statement = stmt_match.group(1).strip() if stmt_match else ""
            
            # Extract current status
            status_match = re.search(r'- \*\*Official Status\*\*:\s*(.+)', full_section)
            analysis_match = re.search(r'- \*\*Barrot Analysis Stage\*\*:\s*(.+)', full_section)
            relevance_match = re.search(r'- \*\*AI/ML Relevance\*\*:\s*(.+)', full_section)
            
            # Extract why it matters
            why_matters = []
            why_section = re.search(r'### Why This Matters for AI\n(.+?)(?=\n###)', full_section, re.DOTALL)
            if why_section:
                for line in why_section.group(1).split('\n'):
                    line = line.strip()
                    if line.startswith('-'):
                        why_matters.append(line[1:].strip())
            
            # Extract Barrot's approach
            approach = []
            approach_section = re.search(r"### Barrot's Approach\n(.+?)(?=\n###)", full_section, re.DOTALL)
            if approach_section:
                for line in approach_section.group(1).split('\n'):
                    line = line.strip()
                    if line and line[0].isdigit() and '.' in line[:3]:
                        # Remove numbering
                        approach.append(re.sub(r'^\d+\.\s+\*\*[^*]+\*\*:\s*', '', line))
            
            # Extract current insights
            insights = []
            insights_section = re.search(r'### Current Insights\n(.+?)(?=\n###)', full_section, re.DOTALL)
            if insights_section:
                for line in insights_section.group(1).split('\n'):
                    line = line.strip()
                    if line.startswith('-'):
                        insights.append(line[1:].strip())
            
            # Extract next steps
            next_steps = []
            steps_section = re.search(r'### Next Steps\n(.+?)(?=\n###)', full_section, re.DOTALL)
            if steps_section:
                for line in steps_section.group(1).split('\n'):
                    line = line.strip()
                    if line.startswith('- ['):
                        next_steps.append(line[5:].strip())  # Remove "- [ ] "
            
            # Extract progress status
            progress_match = re.search(r'### Progress:\s*(.+)', full_section)
            progress_status = progress_match.group(1).strip() if progress_match else ""
            
            problems.append(ProblemDetails(
                number=number,
                name=name,
                problem_statement=problem_statement,
                official_status=status_match.group(1).strip() if status_match else "",
                barrot_analysis_stage=analysis_match.group(1).strip() if analysis_match else "",
                ai_ml_relevance=relevance_match.group(1).strip() if relevance_match else "",
                why_matters_for_ai=why_matters,
                barrot_approach=approach,
                current_insights=insights,
                next_steps=next_steps,
                progress_status=progress_status
            ))
        
        return problems
    
    def extract_progress_metrics(self) -> ProgressMetrics:
        """Extract progress metrics table"""
        metrics_section = re.search(
            r'## 📈 Progress Metrics.+?\| Metric \| Value \|(.+?)(?=\n###|\n##)',
            self.content,
            re.DOTALL
        )
        
        if not metrics_section:
            return ProgressMetrics(
                problems_studied="0/7",
                frameworks_ingested="0/7",
                deep_analysis_started="0/7",
                computational_experiments="0/7",
                publications_reviewed=0,
                novel_insights_generated=0,
                ai_applications_identified=0
            )
        
        metrics_text = metrics_section.group(1)
        
        def extract_metric(metric_name: str) -> str:
            match = re.search(rf'\|\s*{metric_name}\s*\|\s*(.+?)\s*\|', metrics_text)
            return match.group(1).strip() if match else ""
        
        # Safely extract and convert numeric metrics
        ai_apps_str = extract_metric("AI Applications Identified")
        try:
            # Extract first number from string like "3 (P vs NP, Navier-Stokes, Poincaré)"
            ai_apps = int(ai_apps_str.split()[0]) if ai_apps_str and ai_apps_str.split() else 0
        except (ValueError, IndexError):
            ai_apps = 0
        
        return ProgressMetrics(
            problems_studied=extract_metric("Problems Studied"),
            frameworks_ingested=extract_metric("Frameworks Ingested"),
            deep_analysis_started=extract_metric("Deep Analysis Started"),
            computational_experiments=extract_metric("Computational Experiments"),
            publications_reviewed=int(extract_metric("Publications Reviewed") or "0"),
            novel_insights_generated=int(extract_metric("Novel Insights Generated") or "0"),
            ai_applications_identified=ai_apps
        )
    
    def extract_strategic_priorities(self) -> List[StrategicPriority]:
        """Extract strategic priorities"""
        priorities = []
        
        strategy_section = re.search(
            r'## 🎯 Strategic Priorities(.+?)(?=\n\n---)',
            self.content,
            re.DOTALL
        )
        
        if not strategy_section:
            return priorities
        
        strategy_text = strategy_section.group(1)
        
        # Extract High Priority
        high_priority = re.search(
            r'### High Priority \(AI-Relevant\)(.+?)(?=\n\n###|\Z)',
            strategy_text,
            re.DOTALL
        )
        if high_priority:
            problems = []
            for line in high_priority.group(1).split('\n'):
                line = line.strip()
                if line and line[0].isdigit() and '**' in line:
                    match = re.search(r'\*\*(.+?)\*\*', line)
                    if match:
                        problems.append(match.group(1))
            priorities.append(StrategicPriority(
                priority_level="High",
                problems=problems,
                description="AI-Relevant problems with direct impact"
            ))
        
        # Extract Medium Priority
        medium_priority = re.search(
            r'### Medium Priority \(Foundational Understanding\)(.+?)(?=\n\n###|\Z)',
            strategy_text,
            re.DOTALL
        )
        if medium_priority:
            problems = []
            for line in medium_priority.group(1).split('\n'):
                line = line.strip()
                if line and line[0].isdigit() and '**' in line:
                    match = re.search(r'\*\*(.+?)\*\*', line)
                    if match:
                        problems.append(match.group(1))
            priorities.append(StrategicPriority(
                priority_level="Medium",
                problems=problems,
                description="Foundational understanding required"
            ))
        
        # Extract Lower Priority
        lower_priority = re.search(
            r'### Lower Priority \(Long-term Research\)(.+?)(?=\Z)',
            strategy_text,
            re.DOTALL
        )
        if lower_priority:
            problems = []
            for line in lower_priority.group(1).split('\n'):
                line = line.strip()
                if line and line[0].isdigit() and '**' in line:
                    match = re.search(r'\*\*(.+?)\*\*', line)
                    if match:
                        problems.append(match.group(1))
            priorities.append(StrategicPriority(
                priority_level="Lower",
                problems=problems,
                description="Long-term research focus"
            ))
        
        return priorities
    
    def extract_activity_log(self) -> List[Dict[str, str]]:
        """Extract activity log entries"""
        activities = []
        
        activity_section = re.search(
            r'### Activity Log\n(.+?)(?=\n##|---)',
            self.content,
            re.DOTALL
        )
        
        if not activity_section:
            return activities
        
        for line in activity_section.group(1).split('\n'):
            line = line.strip()
            if line.startswith('- **'):
                date_match = re.search(r'\*\*(.+?)\*\*:\s*(.+)', line)
                if date_match:
                    activities.append({
                        "date": date_match.group(1),
                        "activity": date_match.group(2)
                    })
        
        return activities
    
    def generate_search_summaries(self) -> Dict[str, str]:
        """Generate search-ready summaries for key sections"""
        summaries = {}
        
        # Riemann Hypothesis summary for pandas workflows
        riemann = next((p for p in self.problem_details if "Riemann" in p.name), None)
        if riemann:
            summaries["riemann_hypothesis"] = {
                "quick_summary": f"{riemann.problem_statement}",
                "ai_relevance": riemann.ai_ml_relevance,
                "status": riemann.official_status,
                "barrot_stage": riemann.barrot_analysis_stage,
                "computational_approach": "Numerical analysis, pattern detection with ML, statistical analysis of zeros",
                "key_insight": "Billions of zeros computed, all satisfy hypothesis - neural networks could search for patterns",
                "search_tags": ["prime-numbers", "number-theory", "zeta-function", "pattern-recognition", "cryptography"]
            }
        
        # P vs NP summary
        pvsnp = next((p for p in self.problem_details if "P vs NP" in p.name), None)
        if pvsnp:
            summaries["p_vs_np"] = {
                "quick_summary": f"{pvsnp.problem_statement}",
                "ai_relevance": pvsnp.ai_ml_relevance,
                "status": pvsnp.official_status,
                "impact": "Central to computational complexity and algorithm design",
                "ml_connection": "Many ML optimization problems are NP-hard",
                "search_tags": ["complexity-theory", "optimization", "np-complete", "algorithm-design"]
            }
        
        # Navier-Stokes summary
        navier = next((p for p in self.problem_details if "Navier-Stokes" in p.name), None)
        if navier:
            summaries["navier_stokes"] = {
                "quick_summary": f"{navier.problem_statement}",
                "ai_relevance": navier.ai_ml_relevance,
                "status": navier.official_status,
                "practical_use": "Physics-informed neural networks (PINNs) for fluid simulation",
                "research_area": "Turbulence analysis and chaotic systems",
                "search_tags": ["fluid-dynamics", "PINNs", "pde", "simulation", "turbulence"]
            }
        
        return summaries
    
    def create_taxonomy(self) -> Dict[str, Any]:
        """Create classification taxonomy for the problems"""
        taxonomy = {
            "by_ai_applicability": {
                "high": [],
                "medium": [],
                "low": []
            },
            "by_status": {
                "open": [],
                "solved": []
            },
            "by_mathematical_domain": {
                "computer_science": [],
                "number_theory": [],
                "geometry_topology": [],
                "analysis_pde": [],
                "quantum_physics": []
            },
            "by_barrot_priority": {
                "high_priority": [],
                "medium_priority": [],
                "lower_priority": []
            }
        }
        
        # Classify problems
        for overview in self.problems_overview:
            # By AI applicability
            if "High" in overview.ai_applicability:
                taxonomy["by_ai_applicability"]["high"].append(overview.name)
            elif "Medium" in overview.ai_applicability:
                taxonomy["by_ai_applicability"]["medium"].append(overview.name)
            else:
                taxonomy["by_ai_applicability"]["low"].append(overview.name)
            
            # By status
            if "SOLVED" in overview.status:
                taxonomy["by_status"]["solved"].append(overview.name)
            else:
                taxonomy["by_status"]["open"].append(overview.name)
        
        # By mathematical domain (manual classification based on problem nature)
        domain_mapping = {
            "P vs NP": "computer_science",
            "Hodge Conjecture": "geometry_topology",
            "Riemann Hypothesis": "number_theory",
            "Yang-Mills & Mass Gap": "quantum_physics",
            "Navier-Stokes": "analysis_pde",
            "Birch & Swinnerton-Dyer": "number_theory",
            "Poincaré Conjecture": "geometry_topology"
        }
        
        for problem, domain in domain_mapping.items():
            taxonomy["by_mathematical_domain"][domain].append(problem)
        
        # By Barrot priority
        for priority in self.strategic_priorities:
            level_key = priority.priority_level.lower() + "_priority"
            if level_key in taxonomy["by_barrot_priority"]:
                taxonomy["by_barrot_priority"][level_key].extend(priority.problems)
        
        return taxonomy
    
    def execute_ingestion(self) -> Dict[str, Any]:
        """Execute full micro-ingestion pipeline"""
        print("🚀 Starting Millennium Problems Micro-Ingestion...")
        
        if not self.load_document():
            return {"error": "Failed to load document"}
        
        print("📋 Extracting executive summary...")
        self.executive_summary = self.extract_executive_summary()
        
        print("📊 Extracting problems overview table...")
        self.problems_overview = self.extract_problems_overview_table()
        
        print("🔬 Extracting detailed problem information...")
        self.problem_details = self.extract_problem_details()
        
        print("📈 Extracting progress metrics...")
        self.progress_metrics = self.extract_progress_metrics()
        
        print("🎯 Extracting strategic priorities...")
        self.strategic_priorities = self.extract_strategic_priorities()
        
        print("📝 Extracting activity log...")
        self.activity_log = self.extract_activity_log()
        
        print("🔍 Generating search summaries...")
        search_summaries = self.generate_search_summaries()
        
        print("🏷️  Creating taxonomy...")
        taxonomy = self.create_taxonomy()
        
        # Compile complete output
        output = {
            "metadata": {
                "source_document": self.input_file,
                "ingestion_timestamp": datetime.now().isoformat(),
                "ingestion_system": "MillenniumProblemsMicroIngestion v1.0",
                "barrot_agent": "Barrot.Agent"
            },
            "executive_summary": asdict(self.executive_summary) if self.executive_summary else {},
            "problems_overview_table": [asdict(p) for p in self.problems_overview],
            "problem_details": [asdict(p) for p in self.problem_details],
            "progress_metrics": asdict(self.progress_metrics) if self.progress_metrics else {},
            "strategic_priorities": [asdict(p) for p in self.strategic_priorities],
            "activity_log": self.activity_log,
            "search_summaries": search_summaries,
            "taxonomy": taxonomy
        }
        
        print("✅ Micro-ingestion complete!")
        return output
    
    def save_outputs(self, output: Dict[str, Any], output_dir: str = ".") -> None:
        """Save structured outputs to JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save complete output
        complete_file = f"{output_dir}/millennium_problems_ingested_{timestamp}.json"
        with open(complete_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved complete ingestion: {complete_file}")
        
        # Save problems overview table separately
        overview_file = f"{output_dir}/millennium_problems_overview.json"
        with open(overview_file, 'w', encoding='utf-8') as f:
            json.dump(output["problems_overview_table"], f, indent=2, ensure_ascii=False)
        print(f"💾 Saved problems overview: {overview_file}")
        
        # Save search summaries separately
        summaries_file = f"{output_dir}/millennium_problems_search_summaries.json"
        with open(summaries_file, 'w', encoding='utf-8') as f:
            json.dump(output["search_summaries"], f, indent=2, ensure_ascii=False)
        print(f"💾 Saved search summaries: {summaries_file}")
        
        # Save taxonomy separately
        taxonomy_file = f"{output_dir}/millennium_problems_taxonomy.json"
        with open(taxonomy_file, 'w', encoding='utf-8') as f:
            json.dump(output["taxonomy"], f, indent=2, ensure_ascii=False)
        print(f"💾 Saved taxonomy: {taxonomy_file}")
        
        # Save individual problem files for easy access
        # Sanitize filenames to handle special characters safely
        for problem in output["problem_details"]:
            # Remove special characters and sanitize for filesystem
            safe_name = problem['name'].lower()
            # Replace problematic characters
            safe_name = safe_name.replace(' ', '_').replace('&', 'and').replace('✅', '').strip('_')
            # Remove any remaining non-alphanumeric characters except underscore and hyphen
            safe_name = ''.join(c if c.isalnum() or c in '_-' else '' for c in safe_name)
            
            problem_file = f"{output_dir}/millennium_problem_{problem['number']}_{safe_name}.json"
            with open(problem_file, 'w', encoding='utf-8') as f:
                json.dump(problem, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(output['problem_details'])} individual problem files")


def main():
    """Main execution function"""
    print("=" * 80)
    print("🧮 MILLENNIUM PROBLEMS MICRO-INGESTION SYSTEM")
    print("   Barrot.Agent Knowledge Enhancement")
    print("=" * 80)
    print()
    
    ingester = MillenniumProblemsMicroIngestion()
    output = ingester.execute_ingestion()
    
    if "error" in output:
        print(f"❌ Error: {output['error']}")
        return 1
    
    print()
    print("=" * 80)
    print("📊 INGESTION SUMMARY")
    print("=" * 80)
    print(f"Problems in overview table: {len(output['problems_overview_table'])}")
    print(f"Detailed problem analyses: {len(output['problem_details'])}")
    print(f"Strategic priority tiers: {len(output['strategic_priorities'])}")
    print(f"Search summaries generated: {len(output['search_summaries'])}")
    print(f"Activity log entries: {len(output['activity_log'])}")
    print()
    
    ingester.save_outputs(output)
    
    print()
    print("=" * 80)
    print("✅ MICRO-INGESTION COMPLETE")
    print("   All structural components extracted and saved as JSON")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    exit(main())
