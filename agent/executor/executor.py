"""Agent Executor - executes tool calls safely"""
import json
import yaml
from datetime import datetime
from agent.tools.system_tools import SystemTools


class AgentExecutor:
    """Executes planned tool calls with safety checks"""
    
    def __init__(self, config_path="agent/config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.tools = SystemTools(
            timeout=self.config['tools']['timeout_seconds'],
            max_output=self.config['tools']['max_output_size']
        )
        self.dry_run = self.config['safety']['dry_run']
        self.log_actions = self.config['safety']['log_all_actions']
    
    def execute_tool(self, tool_name):
        """Execute a single tool and return results"""
        if self.dry_run:
            return {
                "tool": tool_name,
                "dry_run": True,
                "output": f"DRY RUN: Would execute {tool_name}",
                "timestamp": datetime.now().isoformat()
            }
        
        # Map tool names to methods
        tool_map = {
            "disk_usage": self.tools.disk_usage,
            "cpu_load": self.tools.cpu_load,
            "memory_status": self.tools.memory_status,
            "process_list": self.tools.process_list,
            "recent_errors": self.tools.recent_errors
        }
        
        if tool_name not in tool_map:
            return {
                "tool": tool_name,
                "success": False,
                "output": f"Unknown tool: {tool_name}",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            result = tool_map[tool_name]()
            result["tool"] = tool_name
            return result
        except Exception as e:
            return {
                "tool": tool_name,
                "success": False,
                "output": f"Execution error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_plan(self, plan):
        """Execute all tools in a plan"""
        results = []
        
        for tool_name in plan.get("tools", []):
            result = self.execute_tool(tool_name)
            results.append(result)
            
            if self.log_actions:
                print(f"[{result['timestamp']}] Executed: {tool_name} - Success: {result.get('success', 'N/A')}")
        
        return {
            "plan_goal": plan.get("goal", "Unknown"),
            "tools_executed": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test the executor
    from agent.planner.planner import AgentPlanner
    
    planner = AgentPlanner()
    executor = AgentExecutor()
    
    # Create a test plan
    test_query = "Check system resources"
    print(f"Query: {test_query}\n")
    
    plan = planner.plan(test_query)
    print("Generated Plan:")
    print(json.dumps(plan, indent=2))
    print("\nExecuting plan...\n")
    
    execution_result = executor.execute_plan(plan)
    
    print("\nExecution Summary:")
    print(f"Goal: {execution_result['plan_goal']}")
    print(f"Tools executed: {execution_result['tools_executed']}")
    
    for result in execution_result['results']:
        print(f"\n--- {result['tool']} ---")
        print(f"Success: {result.get('success', 'N/A')}")
        print(f"Output preview: {result['output'][:150]}...")
