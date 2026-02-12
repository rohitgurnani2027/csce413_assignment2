#!/usr/bin/env python3
"""
Port Scanner - Complete Implementation
Assignment 2: Network Security

Features:
- TCP connect scanning
- Multi-threading for faster scans
- Banner grabbing to detect services
- CIDR notation support (e.g., 172.20.0.0/24)
- Progress indicators
- Service fingerprinting
- JSON output format
"""

import argparse
import ipaddress
import json
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional


def grab_banner(target: str, port: int, timeout: float = 2.0) -> Optional[str]:
    """
    Try to grab a banner from an open port
    Some services send banners when you connect
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((target, port))
        
        # Try to get the banner - some services send it automatically
        try:
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            if banner:
                # Just return first 200 chars to keep it reasonable
                return banner[:200]
        except socket.timeout:
            # Service didn't send anything, that's ok
            pass
        
        sock.close()
        return None
    except Exception:
        # Connection failed or something went wrong
        return None


def identify_service(port: int, banner: Optional[str] = None) -> str:
    """
    Figure out what service is running on this port
    Uses port number and banner if available
    """
    # Map of common ports to services
    common_ports = {
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        3306: "MySQL",
        5432: "PostgreSQL",
        6379: "Redis",
        8080: "HTTP-Proxy",
        8443: "HTTPS-Alt",
        5000: "Flask/Development",
        5001: "Flask/Development",
    }
    
    # Check the banner for clues about what service it is
    if banner:
        banner_lower = banner.lower()
        if "ssh" in banner_lower:
            return "SSH"
        elif "http" in banner_lower or "apache" in banner_lower or "nginx" in banner_lower:
            return "HTTP"
        elif "mysql" in banner_lower:
            return "MySQL"
        elif "redis" in banner_lower:
            return "Redis"
        elif "postgres" in banner_lower:
            return "PostgreSQL"
    
    # If we don't know, check common ports or return Unknown
    return common_ports.get(port, "Unknown")


def scan_port(target: str, port: int, timeout: float = 1.0, grab_banner_flag: bool = True) -> Tuple[int, bool, Optional[str], str]:
    """
    Scan a single port - try to connect and see if it's open
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target, port))
        sock.close()
        
        if result == 0:
            # Port is open! Try to get banner if requested
            banner = None
            if grab_banner_flag:
                banner = grab_banner(target, port, timeout)
            service = identify_service(port, banner)
            return (port, True, banner, service)
        else:
            # Port is closed or filtered
            return (port, False, None, "Closed")
            
    except (socket.timeout, ConnectionRefusedError, OSError):
        # Timeout or connection refused means port is closed
        return (port, False, None, "Closed")
    except Exception:
        # Some other error happened
        return (port, False, None, "Error")


def scan_range(target: str, start_port: int, end_port: int, 
               timeout: float = 1.0, threads: int = 100, 
               grab_banner_flag: bool = True, progress: bool = True) -> List[Dict]:
    """
    Scan a range of ports on the target host using multi-threading
    
    Args:
        target: IP address or hostname to scan
        start_port: Starting port number
        end_port: Ending port number
        timeout: Connection timeout in seconds
        threads: Number of concurrent threads
        grab_banner_flag: Whether to attempt banner grabbing
        progress: Whether to show progress
        
    Returns:
        List of dictionaries with scan results
    """
    open_ports = []
    total_ports = end_port - start_port + 1
    scanned = 0
    lock = threading.Lock()
    
    if progress:
        print(f"[*] Scanning {target} from port {start_port} to {end_port} ({total_ports} ports)")
        print(f"[*] Using {threads} threads with {timeout}s timeout")
        print(f"[*] This may take a while...\n")
    
    def update_progress():
        nonlocal scanned
        with lock:
            scanned += 1
            if progress and scanned % 100 == 0:
                percent = (scanned / total_ports) * 100
                print(f"[*] Progress: {scanned}/{total_ports} ports scanned ({percent:.1f}%)", end='\r')
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scan_port, target, port, timeout, grab_banner_flag): port 
                   for port in range(start_port, end_port + 1)}
        
        for future in as_completed(futures):
            port, is_open, banner, service = future.result()
            update_progress()
            
            if is_open:
                result = {
                    "port": port,
                    "state": "open",
                    "service": service,
                    "banner": banner
                }
                open_ports.append(result)
                
                if progress:
                    banner_str = f" - {banner[:50]}" if banner else ""
                    print(f"\n[+] Port {port:5d} is OPEN - {service}{banner_str}")
    
    if progress:
        print(f"\n\n[+] Scan complete!")
        print(f"[+] Found {len(open_ports)} open ports")
    
    return open_ports


def parse_port_range(port_str: str) -> Tuple[int, int]:
    """
    Parse port range string (e.g., "1-1000", "80", "1-65535")
    
    Args:
        port_str: Port range string
        
    Returns:
        Tuple of (start_port, end_port)
    """
    if '-' in port_str:
        start, end = port_str.split('-', 1)
        return (int(start), int(end))
    else:
        port = int(port_str)
        return (port, port)


def expand_cidr(cidr: str) -> List[str]:
    """
    Expand CIDR notation to list of IP addresses
    
    Args:
        cidr: CIDR notation (e.g., "172.20.0.0/24")
        
    Returns:
        List of IP addresses
    """
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError as e:
        print(f"[-] Error parsing CIDR: {e}")
        return []


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Advanced Port Scanner for Network Security Assignment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 -m port_scanner --target 172.20.0.10 --ports 1-1000
  python3 -m port_scanner --target 172.20.0.0/24 --ports 1-10000 --threads 200
  python3 -m port_scanner --target webapp --ports 5000-5010 --json output.json
        """
    )
    
    parser.add_argument(
        "--target",
        required=True,
        help="Target IP address, hostname, or CIDR notation (e.g., 172.20.0.0/24)"
    )
    
    parser.add_argument(
        "--ports",
        default="1-1000",
        help="Port range to scan (e.g., 1-1000, 80, 1-65535). Default: 1-1000"
    )
    
    parser.add_argument(
        "--threads",
        type=int,
        default=100,
        help="Number of concurrent threads. Default: 100"
    )
    
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="Connection timeout in seconds. Default: 1.0"
    )
    
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Disable banner grabbing (faster but less informative)"
    )
    
    parser.add_argument(
        "--json",
        help="Output results to JSON file"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )
    
    args = parser.parse_args()
    
    # Parse port range
    try:
        start_port, end_port = parse_port_range(args.ports)
        if start_port < 1 or end_port > 65535 or start_port > end_port:
            raise ValueError("Invalid port range")
    except ValueError as e:
        print(f"[-] Error: Invalid port range '{args.ports}'. Use format: 1-1000")
        sys.exit(1)
    
    # Check if target is CIDR notation
    if '/' in args.target:
        targets = expand_cidr(args.target)
        if not targets:
            sys.exit(1)
        print(f"[*] Expanded CIDR to {len(targets)} hosts")
    else:
        targets = [args.target]
    
    # Scan each target
    all_results = {}
    
    for target in targets:
        if not args.quiet:
            print(f"\n{'='*60}")
            print(f"Scanning target: {target}")
            print(f"{'='*60}")
        
        results = scan_range(
            target,
            start_port,
            end_port,
            timeout=args.timeout,
            threads=args.threads,
            grab_banner_flag=not args.no_banner,
            progress=not args.quiet
        )
        
        all_results[target] = results
        
        if not args.quiet:
            print(f"\n[+] Summary for {target}:")
            if results:
                for result in results:
                    banner_info = f" | Banner: {result['banner'][:50]}" if result.get('banner') else ""
                    print(f"    Port {result['port']:5d} - {result['service']}{banner_info}")
            else:
                print("    No open ports found")
    
    # Output JSON if requested
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\n[+] Results saved to {args.json}")


if __name__ == "__main__":
    main()
