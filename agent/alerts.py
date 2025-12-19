"""Alert system for the LKO Agent"""
from datetime import datetime
import subprocess
import os


class AlertSystem:
    """Handles alerts and notifications"""
    
    def __init__(self, config):
        self.config = config
        self.alert_enabled = config.get('daemon', {}).get('alerts', {}).get('enabled', True)
        self.thresholds = config.get('daemon', {}).get('alerts', {})
    
    def should_alert(self, metric_type, value):
        """Check if metric exceeds threshold"""
        thresholds = {
            'disk': self.thresholds.get('critical_disk_threshold', 95),
            'memory': self.thresholds.get('critical_memory_threshold', 90),
            'cpu': self.thresholds.get('critical_cpu_threshold', 90)
        }
        
        threshold = thresholds.get(metric_type, 100)
        return value >= threshold
    
    def send_alert(self, alert_type, message, severity="WARNING"):
        """Send alert via configured channels"""
        if not self.alert_enabled:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_msg = f"[{severity}] {timestamp} - {alert_type}: {message}"
        
        # Log to file
        self._log_alert(alert_msg)
        
        # Desktop notification (Ubuntu)
        self._send_desktop_notification(alert_type, message, severity)
        
        return alert_msg
    
    def _log_alert(self, message):
        """Write alert to log file"""
        log_file = "agent/logs/alerts.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, "a") as f:
            f.write(message + "\n")
    
    def _send_desktop_notification(self, title, message, severity):
        """Send Ubuntu desktop notification"""
        try:
            urgency = "critical" if severity == "CRITICAL" else "normal"
            subprocess.run([
                "notify-send",
                "-u", urgency,
                f"LKO Agent: {title}",
                message
            ], timeout=5)
        except:
            pass
    
    def alert_high_disk(self, filesystem, usage_percent):
        """Alert for high disk usage"""
        return self.send_alert(
            "High Disk Usage",
            f"{filesystem} is {usage_percent}% full",
            "CRITICAL" if usage_percent >= 95 else "WARNING"
        )
    
    def alert_high_memory(self, usage_percent):
        """Alert for high memory usage"""
        return self.send_alert(
            "High Memory Usage",
            f"System memory at {usage_percent}%",
            "CRITICAL" if usage_percent >= 90 else "WARNING"
        )
    
    def alert_resource_hog(self, pid, name, reason):
        """Alert for resource-hogging process"""
        return self.send_alert(
            "Resource Hog Detected",
            f"Process {name} (PID {pid}): {reason}",
            "WARNING"
        )
