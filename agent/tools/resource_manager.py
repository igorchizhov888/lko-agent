"""Resource management and remediation tools"""
import subprocess
import time
import psutil
from datetime import datetime


class ResourceManager:
    """Manages system resources with intelligent remediation"""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.remediation_history = []
    
    def get_process_info(self, pid):
        """Get detailed process information"""
        try:
            proc = psutil.Process(pid)
            return {
                "pid": pid,
                "name": proc.name(),
                "cpu_percent": proc.cpu_percent(interval=1),
                "memory_percent": proc.memory_percent(),
                "nice": proc.nice(),
                "status": proc.status(),
                "cmdline": " ".join(proc.cmdline()[:5])
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def find_resource_hogs(self, cpu_threshold=80, memory_threshold=50):
        """Find processes consuming excessive resources"""
        hogs = []
        
        # First pass: initialize cpu_percent for all processes
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc.cpu_percent(interval=0)
            except:
                pass
        
        # Wait a moment for measurements
        import time
        time.sleep(0.5)
        
        # Second pass: get actual CPU usage
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                cpu = proc.cpu_percent(interval=0)
                mem = proc.memory_percent()
                
                if cpu > cpu_threshold or mem > memory_threshold:
                    info = self.get_process_info(proc.info['pid'])
                    if info:
                        info['reason'] = []
                        if cpu > cpu_threshold:
                            info['reason'].append(f"CPU: {cpu:.1f}%")
                        if mem > memory_threshold:
                            info['reason'].append(f"Memory: {mem:.1f}%")
                        hogs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return sorted(hogs, key=lambda x: x['cpu_percent'] + x['memory_percent'], reverse=True)
    
    def renice_process(self, pid, new_nice=19):
        """Reduce process priority"""
        try:
            proc = psutil.Process(pid)
            old_nice = proc.nice()
            
            if old_nice >= new_nice:
                return {"success": False, "action": "renice", "message": f"Process already at nice {old_nice}"}
            
            if self.dry_run:
                return {"success": True, "action": "renice", "dry_run": True, "message": f"DRY RUN: Would renice PID {pid} from {old_nice} to {new_nice}"}
            
            proc.nice(new_nice)
            result = {"success": True, "action": "renice", "pid": pid, "old_nice": old_nice, "new_nice": new_nice, "message": f"Reniced PID {pid}: {old_nice} -> {new_nice}", "timestamp": datetime.now().isoformat()}
            self.remediation_history.append(result)
            return result
        except psutil.NoSuchProcess:
            return {"success": False, "action": "renice", "message": f"Process {pid} not found"}
        except psutil.AccessDenied:
            return {"success": False, "action": "renice", "message": f"Permission denied for PID {pid}"}
    
    def graceful_stop(self, pid, wait_seconds=5):
        """Send SIGTERM and wait for graceful shutdown"""
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            
            if self.dry_run:
                return {"success": True, "action": "graceful_stop", "dry_run": True, "message": f"DRY RUN: Would send SIGTERM to PID {pid} ({name})"}
            
            proc.terminate()
            try:
                proc.wait(timeout=wait_seconds)
                result = {"success": True, "action": "graceful_stop", "pid": pid, "name": name, "message": f"Process {pid} ({name}) stopped gracefully", "timestamp": datetime.now().isoformat()}
            except psutil.TimeoutExpired:
                result = {"success": False, "action": "graceful_stop", "pid": pid, "name": name, "message": f"Process {pid} did not stop after {wait_seconds}s", "timestamp": datetime.now().isoformat()}
            
            self.remediation_history.append(result)
            return result
        except psutil.NoSuchProcess:
            return {"success": False, "action": "graceful_stop", "message": f"Process {pid} not found"}
        except psutil.AccessDenied:
            return {"success": False, "action": "graceful_stop", "message": f"Permission denied for PID {pid}"}
    
    def force_kill(self, pid):
        """Force kill process with SIGKILL (last resort)"""
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            
            if self.dry_run:
                return {"success": True, "action": "force_kill", "dry_run": True, "message": f"DRY RUN: Would send SIGKILL to PID {pid} ({name})"}
            
            proc.kill()
            result = {"success": True, "action": "force_kill", "pid": pid, "name": name, "message": f"Force killed PID {pid} ({name})", "timestamp": datetime.now().isoformat()}
            self.remediation_history.append(result)
            return result
        except psutil.NoSuchProcess:
            return {"success": False, "action": "force_kill", "message": f"Process {pid} already gone"}
        except psutil.AccessDenied:
            return {"success": False, "action": "force_kill", "message": f"Permission denied for PID {pid}"}
    
    def smart_remediate(self, pid, wait_between_steps=10):
        """Intelligent remediation: renice -> graceful -> force"""
        actions = []
        
        print(f"Step 1: Attempting to renice PID {pid}...")
        result = self.renice_process(pid)
        actions.append(result)
        
        if self.dry_run:
            print(f"Step 2: Would attempt graceful stop...")
            result = self.graceful_stop(pid)
            actions.append(result)
            
            print(f"Step 3: Would force kill if graceful failed...")
            result = self.force_kill(pid)
            actions.append(result)
        
        return actions


if __name__ == "__main__":
    print("Testing Resource Manager (DRY RUN MODE)")
    print("="*60)
    
    manager = ResourceManager(dry_run=True)
    print("Finding resource-intensive processes...")
    hogs = manager.find_resource_hogs(cpu_threshold=5, memory_threshold=5)
    
    if hogs:
        print(f"Found {len(hogs)} processes")
        for i, proc in enumerate(hogs[:3], 1):
            print(f"{i}. PID {proc['pid']}: {proc['name']} - {', '.join(proc['reason'])}")
        
        test_pid = hogs[0]['pid']
        print(f"\nTesting on PID {test_pid}")
        results = manager.smart_remediate(test_pid)
        print(f"Result: {results[0]['message']}")
    else:
        print("No resource-intensive processes found")
    
    print("Test complete!")
