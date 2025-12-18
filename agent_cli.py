#!/usr/bin/env python3
"""Main CLI interface for the LKO Agent"""
import sys
import json
import argparse
from agent.planner.planner import AgentPlanner
from agent.executor.executor import AgentExecutor


class LKOAgent:
    """Local Knowledge & Operations Assistant"""
    
    def __init__(self):
        self.planner = AgentPlanner()
        self.executor = AgentExecutor()
    
    def ask(self, query):
        """Process a user query and return results"""
        print(f"\n🤖 Query: {query}\n")
        
        # Planning phase
        print("📋 Planning...")
        plan = self.planner.plan(query)
        
        if "error" in plan:
            print(f"❌ Planning error: {plan.get('reasoning', 'Unknown error')}")
            return
        
        print(f"   Goal: {plan['goal']}")
        print(f"   Tools: {', '.join(plan['tools'])}")
        print(f"   Reasoning: {plan['reasoning']}\n")
        
        # Execution phase
        print("⚙️  Executing...\n")
        results = self.executor.execute_plan(plan)
        
        # Display results
        print("\n" + "="*60)
        print("📊 RESULTS")
        print("="*60)
        
        for result in results['results']:
            tool = result['tool']
            success = result.get('success', False)
            status = "✅" if success else "❌"
            
            print(f"\n{status} {tool.upper()}:")
            print("-" * 60)
            
            output = result.get('output', 'No output')
            # Limit output display
            if len(output) > 1000:
                print(output[:1000])
                print(f"\n... (truncated, {len(output)} total chars)")
            else:
                print(output)
        
        print("\n" + "="*60)
        print(f"✨ Completed: {results['tools_executed']} tools executed")
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Local Knowledge & Operations Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agent ask "Why is disk usage growing?"
  agent ask "What processes are using the most memory?"
  agent ask "Show me recent system errors"
  agent ask "Check system health"
        """
    )
    
    parser.add_argument("command", choices=["ask"], help="Command to execute")
    parser.add_argument("query", help="Your question or request")
    
    args = parser.parse_args()
    
    agent = LKOAgent()
    
    if args.command == "ask":
        agent.ask(args.query)


if __name__ == "__main__":
    main()
