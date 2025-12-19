"""System monitoring tools for the agent"""
import subprocess
import json
from datetime import datetime


class SystemTools:
    """Collection of system monitoring and diagnostic tools"""
    
    def __init__(self, timeout=30, max_output=10000):
        self.timeout = timeout
        self.max_output = max_output
    
    def _run_command(self, cmd):
        """Safely run a shell command with timeout and output limits"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            output = result.stdout[:self.max_output]
            if result.returncode != 0:
                output += f"\nError: {result.stderr[:1000]}"
            
            return {
                "success": result.returncode == 0,
                "output": output,
                "timestamp": datetime.now().isoformat()
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "Command timeout",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"Error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def disk_usage(self):
        """Get disk usage information"""
        return self._run_command("df -h")
    
    def cpu_load(self):
        """Get CPU load information"""
        return self._run_command("uptime && mpstat 1 1 2>/dev/null || top -bn1 | head -20")
    
    def memory_status(self):
        """Get memory usage information"""
        return self._run_command("free -h")
    
    def process_list(self):
        """Get top resource-consuming processes"""
        return self._run_command("ps aux --sort=-%mem | head -20")
    
    def recent_errors(self):
        """Get recent error logs from current boot"""
        return self._run_command("journalctl -b 0 -p err --no-pager 2>/dev/null || tail -100 /var/log/syslog | grep -i error")


if __name__ == "__main__":
    # Test the tools
    tools = SystemTools()
    
    print("Testing disk_usage tool:")
    result = tools.disk_usage()
    print(f"Success: {result['success']}")
    print(result['output'][:200])
