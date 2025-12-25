"""Runbook execution engine - automated response procedures"""
import subprocess
import time
import yaml
from datetime import datetime
from pathlib import Path


class RunbookEngine:
    """Execute automated runbooks based on triggers"""
    
    def __init__(self, config_path="agent/config/runbooks.yaml"):
        self.config_path = config_path
        self.runbooks = []
        self.load_runbooks()
    
    def load_runbooks(self):
        """Load runbooks from config file"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            print(f"Runbook config not found: {self.config_path}")
            return
        
        try:
            with open(config_file) as f:
                config = yaml.safe_load(f)
            
            self.runbooks = config.get('runbooks', [])
            enabled_count = len([r for r in self.runbooks if r.get('enabled', True)])
            print(f"Loaded {len(self.runbooks)} runbooks ({enabled_count} enabled)")
        except Exception as e:
            print(f"Error loading runbooks: {e}")
            self.runbooks = []
    
    def check_trigger(self, runbook, context):
        """Check if runbook trigger conditions are met"""
        if not runbook.get('enabled', True):
            return False
        
        trigger = runbook.get('trigger', {})
        trigger_type = trigger.get('type')
        
        if trigger_type == 'disk_usage':
            return self._check_disk_trigger(trigger, context)
        elif trigger_type == 'memory_usage':
            return self._check_memory_trigger(trigger, context)
        
        return False
    
    def _check_disk_trigger(self, trigger, context):
        """Check disk usage trigger"""
        if 'disk_usage' not in context:
            return False
        
        filesystem = trigger.get('filesystem', '/')
        threshold = trigger.get('threshold', 90)
        operator = trigger.get('operator', '>')
        
        for disk in context['disk_usage']:
            if disk['filesystem'] == filesystem:
                usage = disk['usage_percent']
                
                if operator == '>' and usage > threshold:
                    return True
                elif operator == '>=' and usage >= threshold:
                    return True
        
        return False
    
    def _check_memory_trigger(self, trigger, context):
        """Check memory usage trigger"""
        if 'memory_usage' not in context:
            return False
        
        threshold = trigger.get('threshold', 85)
        operator = trigger.get('operator', '>=')
        usage = context['memory_usage']
        
        if operator == '>=' and usage >= threshold:
            return True
        elif operator == '>' and usage > threshold:
            return True
        
        return False
    
    def execute_runbook(self, runbook, context, dry_run=False):
        """Execute a runbook's actions"""
        name = runbook.get('name', 'unknown')
        actions = runbook.get('actions', [])
        
        print(f"[RUNBOOK] Executing: {name}")
        if dry_run:
            print(f"[RUNBOOK] DRY RUN MODE")
        
        results = {'runbook': name, 'actions': []}
        
        for i, action in enumerate(actions):
            action_type = action.get('type')
            print(f"[RUNBOOK]   Step {i+1}: {action_type}")
            
            if action_type == 'alert':
                result = self._execute_alert(action, dry_run)
            elif action_type == 'command':
                result = self._execute_command(action, dry_run)
            elif action_type == 'wait':
                result = self._execute_wait(action, dry_run)
            else:
                result = {'success': False}
            
            results['actions'].append(result)
        
        return results
    
    def _execute_alert(self, action, dry_run):
        """Execute alert action"""
        message = action.get('message', 'Alert')
        severity = action.get('severity', 'INFO')
        
        if dry_run:
            print(f"[RUNBOOK]     Would alert [{severity}]: {message}")
        else:
            print(f"[RUNBOOK]     Alert [{severity}]: {message}")
        
        return {'success': True, 'type': 'alert'}
    
    def _execute_command(self, action, dry_run):
        """Execute shell command"""
        cmd = action.get('run')
        timeout = action.get('timeout', 30)
        
        if dry_run:
            print(f"[RUNBOOK]     Would run: {cmd}")
            return {'success': True, 'type': 'command', 'dry_run': True}
        
        print(f"[RUNBOOK]     Running: {cmd}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, 
                                   text=True, timeout=timeout)
            success = result.returncode == 0
            print(f"[RUNBOOK]     Command {'succeeded' if success else 'failed'}")
            return {'success': success, 'type': 'command'}
        except:
            return {'success': False, 'type': 'command'}
    
    def _execute_wait(self, action, dry_run):
        """Execute wait action"""
        seconds = action.get('seconds', 5)
        
        if dry_run:
            print(f"[RUNBOOK]     Would wait {seconds}s")
        else:
            print(f"[RUNBOOK]     Waiting {seconds}s...")
            time.sleep(seconds)
        
        return {'success': True, 'type': 'wait'}
    
    def find_matching_runbooks(self, context):
        """Find runbooks matching current context"""
        matching = []
        for runbook in self.runbooks:
            if self.check_trigger(runbook, context):
                matching.append(runbook)
        return matching


if __name__ == "__main__":
    # Test runbook engine
    print("Testing Runbook Engine...")
    print("=" * 60)
    
    engine = RunbookEngine()
    
    # Test with high memory context
    context = {
        'memory_usage': 87.4,
        'disk_usage': [
            {'filesystem': '/home', 'usage_percent': 92}
        ]
    }
    
    print(f"\nTest Context:")
    print(f"  Memory: {context['memory_usage']}%")
    print(f"  /home disk: {context['disk_usage'][0]['usage_percent']}%")
    
    print("\nChecking for matching runbooks...")
    matching = engine.find_matching_runbooks(context)
    
    if matching:
        print(f"\nFound {len(matching)} matching runbooks:")
        for runbook in matching:
            print(f"\n  Runbook: {runbook['name']}")
            print(f"  Description: {runbook['description']}")
            
            print("\n  Executing in DRY RUN mode:")
            print("  " + "-" * 56)
            result = engine.execute_runbook(runbook, context, dry_run=True)
            print("  " + "-" * 56)
    else:
        print("\nNo matching runbooks found")
    
    print("\n" + "=" * 60)
    print("Test complete!")
