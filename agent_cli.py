#!/usr/bin/env python3
"""Main CLI interface for the LKO Agent"""
import sys
import json
import argparse
from agent.planner.planner import AgentPlanner
from agent.executor.executor import AgentExecutor
from agent.memory.incident_logger import IncidentLogger


class LKOAgent:
    """Local Knowledge & Operations Assistant"""
    
    def __init__(self):
        self.planner = AgentPlanner()
        self.executor = AgentExecutor()
        self.logger = IncidentLogger()
    
    def ask(self, query, log_incident=True):
        """Process a user query and return results"""
        print(f"\nQuery: {query}\n")
        
        # Check for similar past incidents first
        print("Checking past incidents...")
        similar = self.logger.search_similar_incidents(query, k=2)
        
        if similar and similar[0][1] > 0.7:  # High similarity threshold
            print("\nFound similar past incident:")
            print("-" * 60)
            meta, score = similar[0]
            print(f"Similarity: {score:.1%}")
            print(f"Previous query: {meta.get('query', 'N/A')}")
            print(f"Goal: {meta.get('goal', 'N/A')}")
            print(f"Outcome: {meta.get('outcome', 'N/A')}")
            print("-" * 60)
            print()
        
        # Planning phase
        print("Planning...")
        plan = self.planner.plan(query)
        
        if "error" in plan:
            print(f"Planning error: {plan.get('reasoning', 'Unknown error')}")
            return
        
        print(f"   Goal: {plan['goal']}")
        print(f"   Tools: {', '.join(plan['tools'])}")
        print(f"   Reasoning: {plan['reasoning']}\n")
        
        # Execution phase
        print("Executing...\n")
        results = self.executor.execute_plan(plan)
        
        # Display results
        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        
        for result in results['results']:
            tool = result['tool']
            success = result.get('success', False)
            status = "SUCCESS" if success else "FAILED"
            
            print(f"\n[{status}] {tool.upper()}:")
            print("-" * 60)
            
            output = result.get('output', 'No output')
            # Limit output display
            if len(output) > 1000:
                print(output[:1000])
                print(f"\n... (truncated, {len(output)} total chars)")
            else:
                print(output)
        
        print("\n" + "="*60)
        print(f"Completed: {results['tools_executed']} tools executed")
        print("="*60 + "\n")
        
        # Log the incident for future reference
        if log_incident:
            outcome = "success" if results['tools_executed'] > 0 else "failure"
            self.logger.log_incident(query, plan, results, outcome=outcome)
            print("(Incident logged for future reference)\n")
    
    def search_history(self, query, k=5):
        """Search past incidents"""
        print(f"\nSearching past incidents for: {query}\n")
        print("="*60)
        
        results = self.logger.search_similar_incidents(query, k=k)
        
        if not results:
            print("No past incidents found.")
            return
        
        for i, (meta, score) in enumerate(results, 1):
            print(f"\nResult {i} (similarity: {score:.1%}):")
            print(f"  Date: {meta.get('timestamp', 'N/A')[:19]}")
            print(f"  Query: {meta.get('query', 'N/A')}")
            print(f"  Goal: {meta.get('goal', 'N/A')}")
            print(f"  Tools: {', '.join(meta.get('tools', []))}")
            print(f"  Outcome: {meta.get('outcome', 'N/A')}")
        
        print("\n" + "="*60 + "\n")
    
    def show_stats(self):
        """Show incident statistics"""
        stats = self.logger.get_statistics()
        
        print("\n" + "="*60)
        print("OPERATIONAL STATISTICS")
        print("="*60)
        print(f"Total incidents logged: {stats['total_incidents']}")
        print(f"Vectors in memory: {stats['vector_count']}")
        
        if stats['total_incidents'] > 0:
            print(f"\nFirst incident: {stats.get('first_incident', 'N/A')[:19]}")
            print(f"Latest incident: {stats.get('latest_incident', 'N/A')[:19]}")
            
            if 'outcomes' in stats:
                print("\nOutcomes:")
                for outcome, count in stats['outcomes'].items():
                    print(f"  {outcome}: {count}")
            
            if 'most_used_tools' in stats and stats['most_used_tools']:
                print("\nMost used tools:")
                for tool, count in stats['most_used_tools']:
                    print(f"  {tool}: {count}x")
        
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Local Knowledge & Operations Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agent_cli.py ask "Why is my disk filling up?"
  agent_cli.py ask "What processes are using the most memory?"
  agent_cli.py search "disk space"
  agent_cli.py stats
        """
    )
    
    parser.add_argument("command", 
                       choices=["ask", "search", "stats", "start", "stop", "status", "restart", "logs"], 
                       help="Command to execute")
    parser.add_argument("query", 
                       nargs='?',
                       help="Your question or search query")
    
    args = parser.parse_args()
    
    agent = LKOAgent()
    
    if args.command == "ask":
        if not args.query:
            print("Error: query required for 'ask' command")
            sys.exit(1)
        agent.ask(args.query)
    
    elif args.command == "search":
        if not args.query:
            print("Error: query required for 'search' command")
            sys.exit(1)
        agent.search_history(args.query)
    
    elif args.command == "stats":
        agent.show_stats()
    
    elif args.command == "start":
        import subprocess
        print("Starting LKO Agent daemon...")
        result = subprocess.run(["sudo", "systemctl", "start", "lko-agent"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Daemon started successfully")
            print("  Use 'agent logs' to view output")
        else:
            print(f"✗ Failed to start: {result.stderr}")
    
    elif args.command == "stop":
        import subprocess
        print("Stopping LKO Agent daemon...")
        result = subprocess.run(["sudo", "systemctl", "stop", "lko-agent"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Daemon stopped successfully")
        else:
            print(f"✗ Failed to stop: {result.stderr}")
    
    elif args.command == "restart":
        import subprocess
        print("Restarting LKO Agent daemon...")
        result = subprocess.run(["sudo", "systemctl", "restart", "lko-agent"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Daemon restarted successfully")
        else:
            print(f"✗ Failed to restart: {result.stderr}")
    
    elif args.command == "status":
        import subprocess
        subprocess.run(["sudo", "systemctl", "status", "lko-agent"])
    
    elif args.command == "logs":
        import subprocess
        print("Showing daemon logs (Ctrl+C to exit)...")
        subprocess.run(["sudo", "journalctl", "-u", "lko-agent", "-f"])


if __name__ == "__main__":
    main()
