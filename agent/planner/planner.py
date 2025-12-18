"""Agent Planner - decides which tools to call based on user query"""
import json
import re
import yaml
from agent.planner.llm import LLMInterface


class AgentPlanner:
    """Plans and generates tool execution steps based on user queries"""
    
    def __init__(self, config_path="agent/config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.llm = LLMInterface(config_path)
        self.available_tools = self.config['tools']['allowed_tools']
    
    def _build_planning_prompt(self, query):
        """Build the prompt for the planner"""
        tools_desc = {
            "disk_usage": "Check disk space usage across filesystems",
            "cpu_load": "Check CPU load and performance metrics",
            "memory_status": "Check RAM and swap memory usage",
            "process_list": "List top memory-consuming processes",
            "recent_errors": "Get recent system error logs"
        }
        
        tools_list = "\n".join([f"- {tool}: {tools_desc.get(tool, '')}" 
                                 for tool in self.available_tools])
        
        prompt = f"""You are a system diagnostics planner. Analyze the user query and decide which tools to use.

Available tools:
{tools_list}

User query: {query}

Respond with ONLY a valid JSON object (no explanation before or after) in this exact format:
{{"goal": "brief description", "tools": ["tool1", "tool2"], "reasoning": "why these tools"}}"""
        
        return prompt
    
    def _extract_json(self, text):
        """Extract first valid JSON object from text"""
        # Try to find JSON object in the response
        match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text
    
    def plan(self, query):
        """Generate a plan for the given query"""
        prompt = self._build_planning_prompt(query)
        
        try:
            response = self.llm.generate(prompt, max_tokens=300)
            
            # Extract JSON from response
            json_text = self._extract_json(response.strip())
            
            plan = json.loads(json_text)
            
            # Validate plan structure
            if not all(k in plan for k in ["goal", "tools", "reasoning"]):
                raise ValueError("Invalid plan structure")
            
            # Filter to allowed tools only
            plan["tools"] = [t for t in plan["tools"] if t in self.available_tools]
            
            return plan
            
        except json.JSONDecodeError as e:
            return {
                "goal": "Parse error",
                "tools": [],
                "reasoning": f"Failed to parse LLM response: {response[:200]}",
                "error": str(e)
            }
        except Exception as e:
            return {
                "goal": "Planning error",
                "tools": [],
                "reasoning": str(e),
                "error": str(e)
            }


if __name__ == "__main__":
    # Test the planner
    planner = AgentPlanner()
    
    test_query = "Why is my disk filling up?"
    print(f"Query: {test_query}\n")
    
    plan = planner.plan(test_query)
    print("Plan:")
    print(json.dumps(plan, indent=2))
