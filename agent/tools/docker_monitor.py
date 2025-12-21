"""Docker container monitoring and management"""
import docker
from datetime import datetime


class DockerMonitor:
    """Monitor Docker containers for resource usage and health"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.available = True
        except docker.errors.DockerException:
            self.available = False
    
    def is_available(self):
        """Check if Docker is available"""
        return self.available
    
    def get_all_containers(self, all_states=True):
        """Get list of all containers"""
        if not self.available:
            return []
        
        try:
            return self.client.containers.list(all=all_states)
        except docker.errors.DockerException:
            return []
    
    def get_container_stats(self, container):
        """Get resource stats for a container"""
        try:
            stats = container.stats(stream=False)
            
            # Calculate CPU percentage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            
            # Calculate memory usage
            mem_usage = stats['memory_stats']['usage']
            mem_limit = stats['memory_stats']['limit']
            mem_percent = (mem_usage / mem_limit) * 100.0 if mem_limit > 0 else 0.0
            
            return {
                'cpu_percent': cpu_percent,
                'memory_usage_mb': mem_usage / (1024 * 1024),
                'memory_limit_mb': mem_limit / (1024 * 1024),
                'memory_percent': mem_percent
            }
        except:
            return None
    
    def get_container_info(self, container):
        """Get detailed container information"""
        try:
            return {
                'id': container.id[:12],
                'name': container.name,
                'image': container.image.tags[0] if container.image.tags else container.image.id[:12],
                'status': container.status,
                'state': container.attrs['State']['Status'],
                'health': container.attrs['State'].get('Health', {}).get('Status', 'none'),
                'restart_policy': container.attrs['HostConfig']['RestartPolicy']['Name'],
                'created': container.attrs['Created']
            }
        except:
            return None
    
    def find_resource_hogs(self, cpu_threshold=80, memory_threshold=80):
        """Find containers using excessive resources"""
        hogs = []
        
        containers = self.get_all_containers(all_states=False)
        
        for container in containers:
            stats = self.get_container_stats(container)
            if not stats:
                continue
            
            info = self.get_container_info(container)
            if not info:
                continue
            
            reasons = []
            if stats['cpu_percent'] > cpu_threshold:
                reasons.append(f"CPU: {stats['cpu_percent']:.1f}%")
            if stats['memory_percent'] > memory_threshold:
                reasons.append(f"Memory: {stats['memory_percent']:.1f}%")
            
            if reasons:
                hogs.append({
                    'container_id': info['id'],
                    'name': info['name'],
                    'image': info['image'],
                    'reasons': reasons,
                    'stats': stats,
                    'info': info
                })
        
        return hogs
    
    def find_unhealthy_containers(self):
        """Find containers in unhealthy or problematic states"""
        issues = []
        
        containers = self.get_all_containers(all_states=True)
        
        for container in containers:
            info = self.get_container_info(container)
            if not info:
                continue
            
            problems = []
            
            # Check if exited without restart policy
            if info['status'] == 'exited' and info['restart_policy'] == 'no':
                problems.append("Exited without restart policy")
            
            # Check health status
            if info['health'] == 'unhealthy':
                problems.append("Health check failing")
            
            # Check if restarting frequently (would need history tracking)
            if info['status'] == 'restarting':
                problems.append("Container restarting")
            
            if problems:
                issues.append({
                    'container_id': info['id'],
                    'name': info['name'],
                    'image': info['image'],
                    'status': info['status'],
                    'problems': problems,
                    'info': info
                })
        
        return issues
    
    def get_summary(self):
        """Get summary of all containers"""
        if not self.available:
            return {"available": False, "error": "Docker not available"}
        
        containers = self.get_all_containers(all_states=True)
        
        summary = {
            "available": True,
            "total": len(containers),
            "running": 0,
            "stopped": 0,
            "paused": 0,
            "restarting": 0,
            "containers": []
        }
        
        for container in containers:
            info = self.get_container_info(container)
            if not info:
                continue
            
            status = info['status']
            if status == 'running':
                summary['running'] += 1
            elif status == 'exited':
                summary['stopped'] += 1
            elif status == 'paused':
                summary['paused'] += 1
            elif status == 'restarting':
                summary['restarting'] += 1
            
            summary['containers'].append({
                'id': info['id'],
                'name': info['name'],
                'image': info['image'],
                'status': status,
                'restart_policy': info['restart_policy']
            })
        
        return summary


if __name__ == "__main__":
    # Test Docker monitoring
    print("Testing Docker Monitor...")
    
    monitor = DockerMonitor()
    
    if not monitor.is_available():
        print("Docker is not available or not running")
        exit(1)
    
    print("\nDocker Summary:")
    summary = monitor.get_summary()
    print(f"  Total containers: {summary['total']}")
    print(f"  Running: {summary['running']}")
    print(f"  Stopped: {summary['stopped']}")
    
    if summary['containers']:
        print("\nContainers:")
        for c in summary['containers']:
            print(f"  - {c['name']} ({c['image']}): {c['status']}")
    
    print("\nChecking for resource hogs...")
    hogs = monitor.find_resource_hogs(cpu_threshold=50, memory_threshold=50)
    if hogs:
        print(f"Found {len(hogs)} resource-intensive containers:")
        for h in hogs:
            print(f"  - {h['name']}: {', '.join(h['reasons'])}")
    else:
        print("No resource hogs detected")
    
    print("\nChecking for unhealthy containers...")
    issues = monitor.find_unhealthy_containers()
    if issues:
        print(f"Found {len(issues)} containers with issues:")
        for i in issues:
            print(f"  - {i['name']}: {', '.join(i['problems'])}")
    else:
        print("All containers healthy")
    
    print("\nDocker monitor test complete!")
