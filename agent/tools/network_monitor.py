"""Network diagnostics and monitoring tools"""
import socket
import subprocess
import psutil
from datetime import datetime


class NetworkMonitor:
    """Monitor network connectivity, ports, and interfaces"""
    
    def __init__(self):
        pass
    
    def ping_host(self, host, count=3, timeout=5):
        """Ping a host and return latency/packet loss"""
        try:
            # Use system ping command
            result = subprocess.run(
                ['ping', '-c', str(count), '-W', str(timeout), host],
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )
            
            output = result.stdout
            
            # Parse output
            stats = {
                'host': host,
                'success': result.returncode == 0,
                'packets_sent': count,
                'packets_received': 0,
                'packet_loss': 100.0,
                'min_ms': None,
                'avg_ms': None,
                'max_ms': None
            }
            
            if result.returncode == 0:
                # Parse: "3 packets transmitted, 3 received, 0% packet loss"
                for line in output.split('\n'):
                    if 'packets transmitted' in line:
                        parts = line.split(',')
                        received = int(parts[1].strip().split()[0])
                        stats['packets_received'] = received
                        stats['packet_loss'] = ((count - received) / count) * 100
                    
                    # Parse: "rtt min/avg/max/mdev = 0.123/0.456/0.789/0.012 ms"
                    if 'rtt min/avg/max' in line or 'round-trip min/avg/max' in line:
                        times = line.split('=')[1].strip().split()[0].split('/')
                        stats['min_ms'] = float(times[0])
                        stats['avg_ms'] = float(times[1])
                        stats['max_ms'] = float(times[2])
            
            return stats
            
        except Exception as e:
            return {
                'host': host,
                'success': False,
                'error': str(e)
            }
    
    def check_port(self, host, port, timeout=3):
        """Check if a port is open on a host"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            return {
                'host': host,
                'port': port,
                'open': result == 0,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'host': host,
                'port': port,
                'open': False,
                'error': str(e)
            }
    
    def check_common_ports(self, host):
        """Check common service ports on a host"""
        common_ports = {
            22: 'SSH',
            80: 'HTTP',
            443: 'HTTPS',
            3306: 'MySQL',
            5432: 'PostgreSQL',
            6379: 'Redis',
            27017: 'MongoDB'
        }
        
        results = []
        for port, service in common_ports.items():
            check = self.check_port(host, port, timeout=2)
            check['service'] = service
            results.append(check)
        
        return results
    
    def get_network_interfaces(self):
        """Get status of all network interfaces"""
        interfaces = []
        
        for interface, addrs in psutil.net_if_addrs().items():
            stats = psutil.net_if_stats()[interface]
            
            ipv4 = None
            ipv6 = None
            
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    ipv4 = addr.address
                elif addr.family == socket.AF_INET6:
                    ipv6 = addr.address
            
            interfaces.append({
                'name': interface,
                'up': stats.isup,
                'speed': stats.speed if stats.speed > 0 else None,
                'ipv4': ipv4,
                'ipv6': ipv6
            })
        
        return interfaces
    
    def get_network_stats(self):
        """Get network traffic statistics"""
        stats = psutil.net_io_counters()
        
        return {
            'bytes_sent': stats.bytes_sent,
            'bytes_recv': stats.bytes_recv,
            'packets_sent': stats.packets_sent,
            'packets_recv': stats.packets_recv,
            'errors_in': stats.errin,
            'errors_out': stats.errout,
            'drops_in': stats.dropin,
            'drops_out': stats.dropout
        }
    
    def get_active_connections(self, kind='inet'):
        """Get active network connections"""
        try:
            connections = psutil.net_connections(kind=kind)
            
            summary = {
                'total': len(connections),
                'established': 0,
                'listening': 0,
                'time_wait': 0,
                'close_wait': 0,
                'connections': []
            }
            
            for conn in connections[:50]:  # Limit to 50 for performance
                if conn.status == 'ESTABLISHED':
                    summary['established'] += 1
                elif conn.status == 'LISTEN':
                    summary['listening'] += 1
                elif conn.status == 'TIME_WAIT':
                    summary['time_wait'] += 1
                elif conn.status == 'CLOSE_WAIT':
                    summary['close_wait'] += 1
                
                summary['connections'].append({
                    'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'status': conn.status,
                    'pid': conn.pid
                })
            
            return summary
            
        except Exception as e:
            return {'error': str(e)}
    
    def check_dns(self, hostname):
        """Check DNS resolution for a hostname"""
        try:
            ip = socket.gethostbyname(hostname)
            return {
                'hostname': hostname,
                'resolved': True,
                'ip': ip,
                'timestamp': datetime.now().isoformat()
            }
        except socket.gaierror as e:
            return {
                'hostname': hostname,
                'resolved': False,
                'error': str(e)
            }
    
    def check_gateway(self):
        """Check if default gateway is reachable"""
        try:
            # Get default gateway
            gateways = psutil.net_if_stats()
            # This is simplified - would need route parsing for actual gateway
            # For now, just ping common gateway
            return self.ping_host('192.168.1.1', count=2, timeout=3)
        except:
            return {'success': False, 'error': 'Could not determine gateway'}


if __name__ == "__main__":
    # Test network monitoring
    print("Testing Network Monitor...")
    print("=" * 60)
    
    monitor = NetworkMonitor()
    
    # Test ping
    print("\nPing Test (google.com):")
    result = monitor.ping_host('google.com', count=3)
    if result['success']:
        print(f"  Success! Avg latency: {result['avg_ms']:.1f}ms, Loss: {result['packet_loss']:.0f}%")
    else:
        print(f"  Failed: {result.get('error', 'Unknown error')}")
    
    # Test port check
    print("\nPort Check (google.com:443):")
    port_result = monitor.check_port('google.com', 443)
    print(f"  Port 443: {'OPEN' if port_result['open'] else 'CLOSED'}")
    
    # Test DNS
    print("\nDNS Resolution (google.com):")
    dns_result = monitor.check_dns('google.com')
    if dns_result['resolved']:
        print(f"  Resolved to: {dns_result['ip']}")
    else:
        print(f"  Failed: {dns_result.get('error')}")
    
    # Test interfaces
    print("\nNetwork Interfaces:")
    interfaces = monitor.get_network_interfaces()
    for iface in interfaces:
        status = "UP" if iface['up'] else "DOWN"
        print(f"  {iface['name']}: {status} - {iface['ipv4']}")
    
    # Test connections
    print("\nActive Connections:")
    conns = monitor.get_active_connections()
    if 'error' not in conns:
        print(f"  Total: {conns['total']}")
        print(f"  Established: {conns['established']}")
        print(f"  Listening: {conns['listening']}")
    
    print("\n" + "=" * 60)
    print("Network monitor test complete!")
