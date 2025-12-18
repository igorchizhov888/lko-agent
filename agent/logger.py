"""Simple logging for the agent"""
import json
from datetime import datetime
from pathlib import Path


class AgentLogger:
    """Log agent queries and results"""
    
    def __init__(self, log_dir="agent/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "queries.jsonl"
    
    def log_query(self, query, plan, results):
        """Log a complete query-plan-result cycle"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "plan": plan,
            "results_summary": {
                "tools_executed": len(results.get("results", [])),
                "success_count": sum(1 for r in results.get("results", []) if r.get("success")),
                "goal": results.get("plan_goal")
            }
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def get_recent_queries(self, n=10):
        """Get the last n queries"""
        if not self.log_file.exists():
            return []
        
        with open(self.log_file) as f:
            lines = f.readlines()
        
        recent = []
        for line in lines[-n:]:
            try:
                recent.append(json.loads(line))
            except:
                pass
        
        return recent
