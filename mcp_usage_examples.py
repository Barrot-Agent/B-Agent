"""
Example Usage: MCP Server Ping for Barrot Agents

This script demonstrates how Barrot agents can utilize the MCP server ping
functionality to enhance their operations and capabilities.
"""

from mcp_server_ping import MCPServerPing
import json
from datetime import datetime


def example_basic_usage():
    """
    Example 1: Basic MCP server ping and analysis
    """
    print("=" * 70)
    print("Example 1: Basic MCP Server Ping")
    print("=" * 70)
    print()
    
    # Create an instance of the MCP ping system
    mcp = MCPServerPing()
    
    # Ping both servers and collect responses
    responses = mcp.collect_all_responses()
    
    print(f"\n✓ Successfully pinged {len(responses)} MCP servers")
    
    # Analyze the capabilities
    analysis = mcp.analyze_capabilities()
    
    print(f"\n✓ Analysis Results:")
    print(f"   - {len(analysis['operational_improvements'])} operational improvements")
    print(f"   - {len(analysis['efficiency_gains'])} efficiency gains")
    print(f"   - {len(analysis['new_opportunities'])} new opportunities")
    print()


def example_playwright_capabilities():
    """
    Example 2: Query Playwright MCP server for specific capabilities
    """
    print("=" * 70)
    print("Example 2: Playwright MCP Server Capabilities")
    print("=" * 70)
    print()
    
    mcp = MCPServerPing()
    playwright_response = mcp.ping_playwright_server()
    
    print("Playwright MCP Server Status:", playwright_response['status'])
    print("\nAvailable Capabilities:")
    for capability, enabled in playwright_response['capabilities'].items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {capability.replace('_', ' ').title()}")
    
    print("\nSupported Browsers:")
    for browser in playwright_response['available_browsers']:
        print(f"  • {browser.title()}")
    
    print("\nPerformance Metrics:")
    metrics = playwright_response['performance_metrics']
    print(f"  • Average Response Time: {metrics['avg_response_time_ms']}ms")
    print(f"  • Success Rate: {metrics['success_rate'] * 100}%")
    print(f"  • Concurrent Sessions: {metrics['concurrent_sessions']}")
    print()


def example_github_capabilities():
    """
    Example 3: Query GitHub MCP server for specific capabilities
    """
    print("=" * 70)
    print("Example 3: GitHub MCP Server Capabilities")
    print("=" * 70)
    print()
    
    mcp = MCPServerPing()
    github_response = mcp.ping_github_server()
    
    print("GitHub MCP Server Status:", github_response['status'])
    print("\nAvailable Capabilities:")
    for capability, enabled in github_response['capabilities'].items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {capability.replace('_', ' ').title()}")
    
    print("\nAPI Features:")
    for feature, available in github_response['api_features'].items():
        status = "✓" if available else "✗"
        print(f"  {status} {feature.replace('_', ' ').title()}")
    
    print("\nRate Limits:")
    limits = github_response['rate_limits']
    print(f"  • Authenticated: {limits['authenticated']} requests/hour")
    print(f"  • Search: {limits['search']} requests/minute")
    print(f"  • Remaining: {limits['remaining']} requests")
    print()


def example_benefits_analysis():
    """
    Example 4: Generate and display benefits analysis
    """
    print("=" * 70)
    print("Example 4: Benefits Analysis")
    print("=" * 70)
    print()
    
    mcp = MCPServerPing()
    mcp.collect_all_responses()
    analysis = mcp.analyze_capabilities()
    
    print("🎯 Top Operational Improvements:")
    print()
    for improvement in analysis['operational_improvements'][:3]:
        print(f"• {improvement['area']} (Impact: {improvement['impact'].upper()})")
        print(f"  └─ {improvement['improvement']}")
    
    print("\n💡 New Opportunities:")
    print()
    for opportunity in analysis['new_opportunities'][:2]:
        print(f"• {opportunity['opportunity']}")
        print(f"  └─ {opportunity['value']}")
    
    print()


def example_save_reports():
    """
    Example 5: Save responses and generate reports for later analysis
    """
    print("=" * 70)
    print("Example 5: Save Reports for Analysis")
    print("=" * 70)
    print()
    
    mcp = MCPServerPing()
    mcp.collect_all_responses()
    mcp.analyze_capabilities()
    
    # Save to custom filenames with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    responses_file = f"mcp_responses_{timestamp}.json"
    report_file = f"MCP_BENEFITS_{timestamp}.md"
    
    mcp.save_responses(responses_file)
    mcp.save_benefits_report(report_file)
    
    print(f"\n✓ Files saved:")
    print(f"  • {responses_file}")
    print(f"  • {report_file}")
    print()


def example_agent_integration():
    """
    Example 6: How an agent would integrate MCP server capabilities
    """
    print("=" * 70)
    print("Example 6: Agent Integration Pattern")
    print("=" * 70)
    print()
    
    # Agent initialization
    print("1. Agent initializes MCP connection...")
    mcp = MCPServerPing()
    
    # Check capabilities before operation
    print("2. Agent checks available capabilities...")
    responses = mcp.collect_all_responses()
    
    # Determine what actions are possible
    playwright_available = any(r['type'] == 'playwright' for r in responses)
    github_available = any(r['type'] == 'github' for r in responses)
    
    print(f"\n✓ Playwright automation: {'Available' if playwright_available else 'Unavailable'}")
    print(f"✓ GitHub integration: {'Available' if github_available else 'Unavailable'}")
    
    # Agent analyzes benefits for decision making
    print("\n3. Agent analyzes benefits...")
    analysis = mcp.analyze_capabilities()
    
    # Agent makes decision based on analysis
    print("\n4. Agent decides on actions based on capabilities:")
    
    if playwright_available:
        print("   • Can perform web automation tasks")
        print("   • Can capture UI screenshots")
        print("   • Can test web applications")
    
    if github_available:
        print("   • Can resolve GitHub issues autonomously")
        print("   • Can monitor workflows")
        print("   • Can search codebases for solutions")
    
    # Agent logs analysis for future reference
    print("\n5. Agent saves analysis for future optimization...")
    mcp.save_responses("agent_mcp_analysis.json")
    
    print("\n✓ Agent successfully integrated MCP capabilities!")
    print()


def main():
    """
    Run all examples to demonstrate MCP server ping usage
    """
    print("\n")
    print("🦜 Barrot-Agent MCP Server Ping Examples")
    print("=" * 70)
    print()
    
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Playwright Capabilities", example_playwright_capabilities),
        ("GitHub Capabilities", example_github_capabilities),
        ("Benefits Analysis", example_benefits_analysis),
        ("Save Reports", example_save_reports),
        ("Agent Integration", example_agent_integration)
    ]
    
    print("Available Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print()
    
    # Run all examples
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"Error in {name}: {e}")
            print()
    
    print("=" * 70)
    print("All examples completed! ✅")
    print("=" * 70)
    print()
    print("Key Takeaways:")
    print("  1. MCP servers provide enhanced capabilities for autonomous operations")
    print("  2. Playwright enables browser automation and UI testing")
    print("  3. GitHub integration supports issue resolution and workflow automation")
    print("  4. Analysis identifies concrete operational improvements and opportunities")
    print("  5. Agents can use MCP capabilities to enhance their decision-making")
    print()
    print("For more details, see:")
    print("  • MCP_BENEFITS_REPORT.md - Comprehensive benefits documentation")
    print("  • mcp_server_responses.json - Raw server responses and analysis")
    print("  • mcp-servers-config.yaml - Configuration and usage guidelines")
    print()


if __name__ == "__main__":
    main()
