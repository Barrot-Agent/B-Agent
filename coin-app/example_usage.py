#!/usr/bin/env python3
"""
Example usage of the Coin App Automation system
Demonstrates how to use the various features
"""

from coin_app_automation import CoinAppAutomation
import json
import time


def demo_check_opportunities():
    """Demo: Check for available opportunities"""
    print("=" * 60)
    print("DEMO: Checking for Opportunities")
    print("=" * 60)
    
    automation = CoinAppAutomation()
    opportunities = automation.check_opportunities()
    
    print(f"\nFound {len(opportunities)} opportunities:")
    for opp in opportunities:
        print(f"\n  {opp['type'].upper()}: {opp.get('title', opp.get('name', opp.get('location')))}")
        print(f"    Estimated Reward: {opp['estimated_reward']} coins")
        print(f"    Estimated Time: {opp['estimated_time']} minutes")
        print(f"    Priority Score: {opp['priority_score']:.2f}")
    
    return opportunities


def demo_execute_task():
    """Demo: Execute a single task"""
    print("\n" + "=" * 60)
    print("DEMO: Executing a Task")
    print("=" * 60)
    
    automation = CoinAppAutomation()
    opportunities = automation.check_opportunities()
    
    if opportunities:
        # Execute the highest priority opportunity
        prioritized = automation._prioritize_opportunities(opportunities)
        top_opportunity = prioritized[0]
        
        print(f"\nExecuting: {top_opportunity['type']} - {top_opportunity.get('title', top_opportunity.get('name', 'Task'))}")
        result = automation.execute_task(top_opportunity)
        
        print(f"\nResult:")
        print(json.dumps(result, indent=2))
        
        return result
    else:
        print("\nNo opportunities available to execute")
        return None


def demo_earnings_report():
    """Demo: Generate earnings report"""
    print("\n" + "=" * 60)
    print("DEMO: Earnings Report")
    print("=" * 60)
    
    automation = CoinAppAutomation()
    
    # Execute a few tasks to have some data
    opportunities = automation.check_opportunities()
    for opp in opportunities[:2]:  # Execute 2 tasks
        automation.execute_task(opp)
    
    # Generate report
    report = automation.get_earnings_report("today")
    
    print("\nToday's Earnings Report:")
    print(json.dumps(report, indent=2))
    
    return report


def demo_full_cycle():
    """Demo: One complete automation cycle"""
    print("\n" + "=" * 60)
    print("DEMO: Full Automation Cycle")
    print("=" * 60)
    
    automation = CoinAppAutomation()
    
    print("\n1. Checking for opportunities...")
    opportunities = automation.check_opportunities()
    print(f"   Found: {len(opportunities)} opportunities")
    
    print("\n2. Prioritizing opportunities...")
    prioritized = automation._prioritize_opportunities(opportunities)
    print(f"   Top priority: {prioritized[0]['type']} ({prioritized[0]['priority_score']:.2f})")
    
    print("\n3. Executing top 3 opportunities...")
    for i, opp in enumerate(prioritized[:3], 1):
        print(f"\n   Task {i}/{3}: {opp['type']}")
        result = automation.execute_task(opp)
        if result['status'] == 'success':
            print(f"   ✓ Success! Earned {result['coins_earned']} coins")
        else:
            print(f"   ✗ Failed: {result.get('message', 'Unknown error')}")
    
    print("\n4. Generating earnings report...")
    report = automation.get_earnings_report("today")
    print(f"   Total earnings today: {report['total_coins']} coins")
    
    print("\n✓ Full automation cycle completed!")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 8 + "Coin App Automation - Example Usage" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    
    try:
        # Demo 1: Check opportunities
        demo_check_opportunities()
        time.sleep(1)
        
        # Demo 2: Execute a task
        demo_execute_task()
        time.sleep(1)
        
        # Demo 3: Earnings report
        demo_earnings_report()
        time.sleep(1)
        
        # Demo 4: Full cycle
        demo_full_cycle()
        
        print("\n" + "=" * 60)
        print("All demos completed successfully! 🎉")
        print("=" * 60)
        print("\nTo run in production mode:")
        print("  python coin_app_automation.py")
        print("\nTo generate a report:")
        print("  python coin_app_automation.py --report")
        print("\nTo run in aggressive mode:")
        print("  python coin_app_automation.py --mode=aggressive")
        print("")
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
