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


    def get_networks(self):
        """Get all Docker networks"""
        if not self.available:
            return []
        
        try:
            networks = self.client.networks.list()
            network_info = []
            
            for net in networks:
                try:
                    # Reload network to get fresh data
                    net.reload()
                    
                    # Safely get IPAM config
                    ipam = net.attrs.get('IPAM', {})
                    config = ipam.get('Config', [])
                    subnet = config[0].get('Subnet', 'N/A') if config else 'N/A'
                    
                    network_info.append({
                        'id': net.id[:12],
                        'name': net.name,
                        'driver': net.attrs.get('Driver', 'unknown'),
                        'scope': net.attrs.get('Scope', 'unknown'),
                        'containers': len(net.attrs.get('Containers', {})),
                        'subnet': subnet
                    })
                except Exception as e:
                    # Skip this network but continue with others
                    print(f"Warning: Could not parse network {net.name}: {e}")
                    continue
            
            return network_info
        except Exception as e:
            print(f"Error getting networks: {e}")
            return []
    
    def get_network_containers(self, network_name):
        """Get all containers on a specific network"""
        if not self.available:
            return []
        
        try:
            network = self.client.networks.get(network_name)
            containers_info = []
            
            for container_id, container_data in network.attrs['Containers'].items():
                containers_info.append({
                    'id': container_id[:12],
                    'name': container_data['Name'],
                    'ipv4': container_data.get('IPv4Address', 'N/A').split('/')[0],
                    'ipv6': container_data.get('IPv6Address', 'N/A').split('/')[0] if container_data.get('IPv6Address') else None
                })
            
            return containers_info
        except:
            return []
    
    def check_container_connectivity(self, source_container_name, target_container_name):
        """Check if one container can reach another"""
        if not self.available:
            return {'success': False, 'error': 'Docker not available'}
        
        try:
            source = self.client.containers.get(source_container_name)
            
            # Only works if source container is running
            if source.status != 'running':
                return {
                    'success': False,
                    'source': source_container_name,
                    'target': target_container_name,
                    'error': 'Source container not running'
                }
            
            # Try to ping target container by name (Docker DNS)
            result = source.exec_run(f"ping -c 2 -W 2 {target_container_name}")
            
            return {
                'success': result.exit_code == 0,
                'source': source_container_name,
                'target': target_container_name,
                'exit_code': result.exit_code,
                'output': result.output.decode('utf-8') if result.output else ''
            }
        except Exception as e:
            return {
                'success': False,
                'source': source_container_name,
                'target': target_container_name,
                'error': str(e)
            }
    
    def check_network_health(self, network_name):
        """Check overall health of a Docker network"""
        if not self.available:
            return {'healthy': False, 'error': 'Docker not available'}
        
        try:
            network = self.client.networks.get(network_name)
            containers = self.get_network_containers(network_name)
            
            # Check if network exists and has containers
            health = {
                'name': network_name,
                'healthy': True,
                'driver': network.attrs['Driver'],
                'containers_count': len(containers),
                'issues': []
            }
            
            # Check for issues
            if len(containers) == 0:
                health['issues'].append('No containers on network')
            
            # Check if network is internal (no external connectivity)
            if network.attrs.get('Internal', False):
                health['issues'].append('Network is internal (no external access)')
            
            if health['issues']:
                health['healthy'] = False
            
            return health
            
        except Exception as e:
            return {
                'name': network_name,
                'healthy': False,
                'error': str(e)
            }
    
    def get_network_summary(self):
        """Get comprehensive network summary"""
        if not self.available:
            return {'available': False}
        
        networks = self.get_networks()
        
        summary = {
            'available': True,
            'total_networks': len(networks),
            'networks': []
        }
        
        for net in networks:
            net_detail = {
                'name': net['name'],
                'driver': net['driver'],
                'containers': net['containers'],
                'subnet': net['subnet']
            }
            
            # Get containers on this network
            if net['containers'] > 0:
                net_detail['container_list'] = self.get_network_containers(net['name'])
            
            summary['networks'].append(net_detail)
        
        return summary



if __name__ == "__main__":
    print("Testing Docker Monitor...")
    
    monitor = DockerMonitor()
    
    if not monitor.is_available():
        print("Docker not available")
        exit(1)
    
    print("\nDocker Networks:")
    summary = monitor.get_network_summary()
    print(f"Total networks: {summary['total_networks']}")
    
    for net in summary['networks']:
        print(f"  {net['name']}: {net['containers']} containers")
    
    print("\nTest complete!")
