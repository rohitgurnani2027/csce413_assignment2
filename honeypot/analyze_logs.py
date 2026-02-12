#!/usr/bin/env python3
"""
Analyze honeypot logs and generate statistics
"""

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("/app/logs/connections.jsonl")


def load_logs():
    """Load all logs from JSONL file"""
    if not LOG_FILE.exists():
        return []
    
    logs = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            if line.strip():
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    
    return logs


def analyze_logs():
    """Analyze honeypot logs and generate report"""
    logs = load_logs()
    
    if not logs:
        print("No logs found. Start the honeypot and generate some attacks first.")
        return
    
    print("="*60)
    print("Honeypot Log Analysis")
    print("="*60)
    print()
    
    # Basic statistics
    total_events = len(logs)
    unique_ips = set(log.get("source_ip") for log in logs)
    event_types = Counter(log.get("event_type") for log in logs)
    
    print("📊 Basic Statistics")
    print("-" * 60)
    print(f"Total Events: {total_events}")
    print(f"Unique IP Addresses: {len(unique_ips)}")
    print(f"Event Types: {dict(event_types)}")
    print()
    
    # Connection analysis
    connections = [log for log in logs if log.get("event_type") == "connection_start"]
    print(f"📡 Connections: {len(connections)}")
    print()
    
    # Authentication analysis
    auth_attempts = [log for log in logs if log.get("event_type") == "authentication_attempt"]
    if auth_attempts:
        print("🔐 Authentication Attempts")
        print("-" * 60)
        print(f"Total Attempts: {len(auth_attempts)}")
        
        usernames = Counter(log.get("username", "unknown") for log in auth_attempts)
        passwords = Counter(log.get("password", "unknown") for log in auth_attempts)
        
        print(f"\nTop Usernames:")
        for username, count in usernames.most_common(10):
            print(f"  {username}: {count}")
        
        print(f"\nTop Passwords:")
        for password, count in passwords.most_common(10):
            masked = "*" * len(password) if len(password) > 3 else "***"
            print(f"  {masked}: {count}")
        
        failed = sum(1 for log in auth_attempts if not log.get("success", False))
        successful = sum(1 for log in auth_attempts if log.get("success", False))
        print(f"\nFailed: {failed}")
        print(f"Successful: {successful}")
        print()
    
    # Command analysis
    commands = [log for log in logs if log.get("event_type") == "command_executed"]
    if commands:
        print("💻 Commands Executed")
        print("-" * 60)
        print(f"Total Commands: {len(commands)}")
        
        cmd_list = [log.get("command", "unknown")[:50] for log in commands]
        cmd_counter = Counter(cmd_list)
        
        print("\nTop Commands:")
        for cmd, count in cmd_counter.most_common(10):
            print(f"  {cmd}: {count}")
        print()
    
    # IP analysis
    print("🌐 IP Address Analysis")
    print("-" * 60)
    ip_events = Counter(log.get("source_ip") for log in logs)
    
    print("Top Source IPs:")
    for ip, count in ip_events.most_common(10):
        print(f"  {ip}: {count} events")
    print()
    
    # Timeline
    print("⏰ Timeline")
    print("-" * 60)
    if logs:
        first_event = min(log.get("timestamp", "") for log in logs)
        last_event = max(log.get("timestamp", "") for log in logs)
        print(f"First Event: {first_event}")
        print(f"Last Event: {last_event}")
    print()
    
    # Attack patterns
    print("🎯 Attack Patterns Detected")
    print("-" * 60)
    
    # Brute force detection (multiple failed attempts from same IP)
    ip_auth_counts = defaultdict(int)
    for log in auth_attempts:
        if not log.get("success", False):
            ip_auth_counts[log.get("source_ip")] += 1
    
    brute_force_ips = [ip for ip, count in ip_auth_counts.items() if count >= 3]
    if brute_force_ips:
        print(f"⚠️  Brute Force Attacks Detected from {len(brute_force_ips)} IP(s):")
        for ip in brute_force_ips:
            print(f"  {ip}: {ip_auth_counts[ip]} failed attempts")
    else:
        print("✅ No obvious brute force patterns detected")
    print()
    
    print("="*60)
    print("Analysis Complete")
    print("="*60)


if __name__ == "__main__":
    analyze_logs()

