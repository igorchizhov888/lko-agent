#!/usr/bin/env python3
"""LKO Agent Daemon - Autonomous monitoring service"""
import time
import signal
import sys
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.planner.planner import AgentPlanner
from agent.executor.executor import AgentExecutor
from agent.memory.incident_logger import IncidentLogger
from agent.tools.resource_manager import ResourceManager
from agent.alerts import AlertSystem
from agent.log_rotation import LogRotation
import yaml


class AgentDaemon:
    """Autonomous monitoring daemon"""
    
    def __init__(self, config_path="agent/config.yaml"):
        self.running = False
        self.config_path = config_path
        self.load_config()
        
        # Initialize components
        self.planner = AgentPlanner(config_path)
        self.executor = AgentExecutor(config_path)
        self.logger = IncidentLogger()
        self.resource_manager = ResourceManager(dry_run=False)
        self.alerts = AlertSystem(self.config)
        self.log_rotation = LogRotation(max_size_mb=100, max_age_days=30)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)
        
        print(f"[{self.timestamp()}] LKO Agent Daemon initialized")
    
    def load_config(self):
        """Load daemon configuration"""
        with open(self.config_path) as f:
            self.config = yaml.safe_load(f)
        
        # Daemon-specific config (we'll add this to config.yaml)
        self.check_interval = self.config.get('daemon', {}).get('check_interval', 3600)  # 1 hour default
        self.health_check_interval = self.config.get('daemon', {}).get('health_check_interval', 21600)  # 6 hours
        self.resource_check_interval = self.config.get('daemon', {}).get('resource_check_interval', 300)  # 5 min
    
    def timestamp(self):
        """Current timestamp for logging"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def handle_shutdown(self, signum, frame):
        """Graceful shutdown handler"""
        print(f"\n[{self.timestamp()}] Received shutdown signal, stopping gracefully...")
        self.running = False
    
    def run_health_check(self):
        """Execute full system health check"""
        print(f"[{self.timestamp()}] Running full health check...")
        
        query = "Perform comprehensive system health check"
        plan = self.planner.plan(query)
        results = self.executor.execute_plan(plan)
        
        # Log the check
        self.logger.log_incident(query, plan, results, outcome="success", 
                                notes="Autonomous health check")
        
        print(f"[{self.timestamp()}] Health check complete: {results['tools_executed']} tools executed")
        return results
    
    def check_resources(self):
        """Check for resource hogs"""
        print(f"[{self.timestamp()}] Checking resource usage...")
        
        hogs = self.resource_manager.find_resource_hogs(
            cpu_threshold=80,
            memory_threshold=50
        )
        
        if hogs:
            print(f"[{self.timestamp()}] WARNING: Found {len(hogs)} resource-intensive processes")
            for proc in hogs[:3]:
                print(f"  - PID {proc['pid']}: {proc['name']} - {', '.join(proc['reason'])}")
                # Send alert for resource hog
                self.alerts.alert_resource_hog(proc['pid'], proc['name'], ', '.join(proc['reason']))
                
                # Attempt smart remediation (renice -> graceful -> force)
                print(f"[{self.timestamp()}] Attempting remediation for PID {proc['pid']}...")
                remediation_results = self.resource_manager.smart_remediate(proc['pid'])
                for result in remediation_results:
                    print(f"[{self.timestamp()}]   {result['action']}: {result['message']}")
            
            # Log as incident
            query = f"High resource usage detected: {len(hogs)} processes"
            plan = {"goal": "Resource monitoring", "tools": ["process_list"], "reasoning": "Autonomous check"}
            results = {"tools_executed": 1, "results": [{"tool": "resource_manager", "success": True}]}
            self.logger.log_incident(query, plan, results, outcome="warning",
                                   notes=f"Found {len(hogs)} resource hogs")
        else:
            print(f"[{self.timestamp()}] Resource usage normal")
        
        return hogs
    
    def run(self):
        """Main daemon loop"""
        self.running = True
        last_health_check = 0
        last_resource_check = 0
        
        print(f"[{self.timestamp()}] LKO Agent Daemon started")
        print(f"[{self.timestamp()}] Health checks every {self.health_check_interval}s")
        print(f"[{self.timestamp()}] Resource checks every {self.resource_check_interval}s")
        print(f"[{self.timestamp()}] Press Ctrl+C to stop")
        
        try:
            while self.running:
                current_time = time.time()
                
                # Time for health check?
                if current_time - last_health_check >= self.health_check_interval:
                    self.run_health_check()
                    last_health_check = current_time
                
                # Time for resource check?
                if current_time - last_resource_check >= self.resource_check_interval:
                    self.check_resources()
                    last_resource_check = current_time
                
                # Sleep for a bit
                time.sleep(60)  # Check every minute if it's time to do something
                
        except Exception as e:
            print(f"[{self.timestamp()}] ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print(f"[{self.timestamp()}] LKO Agent Daemon stopped")


def main():
    daemon = AgentDaemon()
    daemon.run()


if __name__ == "__main__":
    main()
