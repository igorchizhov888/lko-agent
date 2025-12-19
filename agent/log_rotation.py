"""Log rotation and cleanup utilities"""
import os
from pathlib import Path
from datetime import datetime, timedelta


class LogRotation:
    """Manages log file rotation and cleanup"""
    
    def __init__(self, max_size_mb=100, max_age_days=30):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_age_days = max_age_days
    
    def rotate_if_needed(self, log_file):
        """Rotate log file if it exceeds size limit"""
        log_path = Path(log_file)
        
        if not log_path.exists():
            return False
        
        size = log_path.stat().st_size
        
        if size > self.max_size_bytes:
            old_path = log_path.with_suffix(log_path.suffix + '.old')
            
            if old_path.exists():
                old_path.unlink()
            
            log_path.rename(old_path)
            
            print(f"Rotated {log_file} ({size / 1024 / 1024:.1f}MB)")
            return True
        
        return False
    
    def cleanup_old_logs(self, log_dir):
        """Remove log files older than max_age_days"""
        log_path = Path(log_dir)
        
        if not log_path.exists():
            return []
        
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
        removed = []
        
        for log_file in log_path.glob('*.log.old'):
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if mtime < cutoff_date:
                log_file.unlink()
                removed.append(str(log_file))
        
        return removed
    
    def rotate_all_logs(self):
        """Rotate all agent logs"""
        logs = [
            "agent/logs/agent.log",
            "agent/logs/alerts.log",
            "agent/logs/incidents.jsonl",
            "agent/logs/daemon.log"
        ]
        
        rotated = []
        for log in logs:
            if self.rotate_if_needed(log):
                rotated.append(log)
        
        removed = self.cleanup_old_logs("agent/logs")
        
        return {"rotated": rotated, "removed": removed}
