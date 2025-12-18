#!/usr/bin/env python3
"""Display agent status and capabilities"""
import yaml
from pathlib import Path

def show_status():
    print("="*70)
    print("  LKO AGENT - Local Knowledge & Operations Assistant")
    print("="*70)
    
    # Load config
    config_path = Path("agent/config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        print("\nConfiguration:")
        print(f"   Mode: {config['agent']['mode']}")
        print(f"   Dry Run: {config['safety']['dry_run']}")
        print(f"   LLM: Phi-3 Mini (Q4)")
        print(f"   Threads: {config['llm']['threads']}")
        print(f"   Temperature: {config['llm']['temperature']}")
        
        print("\nAvailable Tools:")
        for tool in config['tools']['allowed_tools']:
            print(f"   * {tool}")
        
        print("\nCurrent Capabilities:")
        print("   * Natural language system diagnostics")
        print("   * Intelligent tool selection")
        print("   * Safe command execution")
        print("   * Activity logging")
        
        print("\nQuick Start:")
        print('   python3 agent_cli.py ask "Why is my disk filling up?"')
        print('   python3 agent_cli.py ask "What processes use most memory?"')
        print('   python3 agent_cli.py ask "Is my system healthy?"')
        
        print("\nNext Steps (Not Yet Implemented):")
        print("   - Memory & RAG system")
        print("   - Autonomous scheduling")
        print("   - Automated remediation")
        print("   - Custom runbook integration")
        
        print("\n" + "="*70)
        print("  Status: MVP Complete - Ready for testing!")
        print("="*70 + "\n")
    else:
        print("ERROR: Config not found. Run from project root.")

if __name__ == "__main__":
    show_status()
