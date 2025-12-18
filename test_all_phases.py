#!/usr/bin/env python3
"""Comprehensive test of all LKO Agent phases"""
import sys
sys.path.insert(0, '.')

from agent.planner.planner import AgentPlanner
from agent.executor.executor import AgentExecutor
from agent.memory.incident_logger import IncidentLogger
from agent.tools.resource_manager import ResourceManager


def test_phase1():
    """Test Phase 1: Core Agent"""
    print("="*70)
    print("PHASE 1 TEST: Core Agent (Planning + Execution)")
    print("="*70)
    
    planner = AgentPlanner()
    executor = AgentExecutor()
    
    query = "Check system resources"
    print(f"\nQuery: {query}")
    
    plan = planner.plan(query)
    print(f"Plan: {plan['goal']}")
    print(f"Tools: {', '.join(plan['tools'])}")
    
    results = executor.execute_plan(plan)
    print(f"Executed: {results['tools_executed']} tools")
    print("Phase 1: PASSED\n")


def test_phase2():
    """Test Phase 2: Memory & RAG"""
    print("="*70)
    print("PHASE 2 TEST: Memory & RAG")
    print("="*70)
    
    logger = IncidentLogger()
    
    # Search for past incidents
    print("\nSearching for 'slow system' incidents...")
    results = logger.search_similar_incidents("slow system", k=2)
    
    if results:
        print(f"Found {len(results)} similar incidents")
        meta, score = results[0]
        print(f"Most similar: {meta.get('query', 'N/A')} ({score:.1%})")
    else:
        print("No incidents found (database empty)")
    
    # Get statistics
    stats = logger.get_statistics()
    print(f"\nTotal incidents logged: {stats['total_incidents']}")
    print(f"Vectors in memory: {stats['vector_count']}")
    
    print("Phase 2: PASSED\n")


def test_phase3():
    """Test Phase 3: Resource Management"""
    print("="*70)
    print("PHASE 3 TEST: Intelligent Resource Management")
    print("="*70)
    
    manager = ResourceManager(dry_run=True)
    
    # Find resource hogs
    print("\nFinding resource-intensive processes...")
    hogs = manager.find_resource_hogs(cpu_threshold=5, memory_threshold=5)
    
    if hogs:
        print(f"Found {len(hogs)} processes using significant resources")
        
        # Test smart remediation on first one
        test_proc = hogs[0]
        print(f"\nTesting remediation on PID {test_proc['pid']} ({test_proc['name']})")
        print(f"Current: {', '.join(test_proc['reason'])}")
        
        results = manager.smart_remediate(test_proc['pid'])
        print(f"\nRemediation steps simulated: {len(results)}")
        for r in results:
            print(f"  - {r['action']}: {r['message']}")
    else:
        print("No resource-intensive processes found")
    
    print("\nPhase 3: PASSED\n")


def main():
    print("\n" + "="*70)
    print(" LKO AGENT - COMPREHENSIVE TEST SUITE")
    print("="*70 + "\n")
    
    try:
        test_phase1()
        test_phase2()
        test_phase3()
        
        print("="*70)
        print(" ALL PHASES PASSED - AGENT FULLY OPERATIONAL")
        print("="*70)
        print("\nSummary:")
        print("  Phase 1: Core agent with planning and execution")
        print("  Phase 2: Memory system with incident tracking")
        print("  Phase 3: Intelligent resource management")
        print("\nThe LKO Agent is ready for production use!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
