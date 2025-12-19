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
        print(f"   Version: 0.4.0")
        print(f"   Mode: {config['agent']['mode']}")
        print(f"   Dry Run: {config['safety']['dry_run']}")
        print(f"   LLM: Phi-3 Mini (Q4)")
        
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
        
        print("\nPhase 4 - Autonomous Operation: COMPLETE")
        print("   * Systemd service with auto-restart")
        print("   * Scheduled health checks (6 hours)")
        print("   * Resource monitoring (5 minutes)")
        print("   * Desktop alert notifications")
        print("   * Automatic log rotation")
        
        print("\nDaemon Commands:")
        print("   agent start   - Start autonomous monitoring")
        print("   agent stop    - Stop daemon")
        print("   agent status  - Check daemon status")
        print("   agent restart - Restart daemon")
        print("   agent logs    - View live logs")
        
        print("\nQuery Commands:")
        print("   agent ask \"your question\"")
        print("   agent search \"keyword\"")
        print("   agent stats")
        
        print("\n" + "="*70)
        print("  Status: ALL 4 PHASES COMPLETE - PRODUCTION READY")
        print("="*70 + "\n")
    else:
        print("ERROR: Config not found. Run from project root.")

if __name__ == "__main__":
    show_status()
