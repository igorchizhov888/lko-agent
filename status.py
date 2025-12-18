#!/usr/bin/env python3
"""Display agent status and capabilities"""
import yaml
from pathlib import Path

def show_status():
    print("="*70)
    print("  LKO AGENT - Local Knowledge & Operations Assistant")
    print("="*70)
    
    config_path = Path("agent/config.yaml")
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        print("\nConfiguration:")
        print(f"   Version: 0.3.0")
        print(f"   Mode: {config['agent']['mode']}")
        print(f"   Dry Run: {config['safety']['dry_run']}")
        print(f"   LLM: Phi-3 Mini (Q4)")
        print(f"   Threads: {config['llm']['threads']}")
        
        print("\nPhase 1 - Core Agent: COMPLETE")
        print("   * Natural language system diagnostics")
        print("   * Intelligent LLM-based planning")
        print("   * Safe tool execution")
        
        print("\nPhase 2 - Memory & RAG: COMPLETE")
        print("   * FAISS vector store with semantic search")
        print("   * Incident logging and history tracking")
        print("   * Pattern recognition over time")
        
        print("\nPhase 3 - Resource Management: COMPLETE")
        print("   * Smart three-tier remediation")
        print("   * Renice -> Graceful -> Force kill")
        print("   * Process monitoring and control")
        
        print("\nAvailable Commands:")
        print("   agent ask \"your question\"")
        print("   agent search \"keyword\"")
        print("   agent stats")
        print("   python3 test_all_phases.py")
        
        print("\nSystem Tools:")
        for tool in config['tools']['allowed_tools']:
            print(f"   * {tool}")
        
        print("\nNext Steps (Phase 4):")
        print("   - Systemd service for autonomous operation")
        print("   - Scheduled health checks")
        print("   - Proactive monitoring and alerts")
        
        print("\n" + "="*70)
        print("  Status: PRODUCTION READY - All 3 Phases Complete")
        print("="*70 + "\n")
    else:
        print("ERROR: Config not found. Run from project root.")

if __name__ == "__main__":
    show_status()
