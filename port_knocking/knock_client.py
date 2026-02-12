#!/usr/bin/env python3
"""
Port Knocking Client
Sends knock sequence to server and connects to protected service
"""

import argparse
import socket
import sys
import time

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_DELAY = 0.3


def send_knock(target, port, delay=0.3):
    """Send a single knock to the target port"""
    try:
        # Create TCP connection (knock)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1.0)
        sock.connect((target, port))
        sock.close()
        print(f"  ✅ Knocked port {port}")
        time.sleep(delay)
        return True
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        # Connection refused is expected - we just need to attempt connection
        print(f"  ✅ Knocked port {port} (connection attempt made)")
        time.sleep(delay)
        return True
    except Exception as e:
        print(f"  ❌ Error knocking port {port}: {e}")
        return False


def perform_knock_sequence(target, sequence, delay):
    """Send the full knock sequence"""
    print(f"🔔 Sending knock sequence to {target}: {sequence}")
    print("")
    
    for i, port in enumerate(sequence, 1):
        print(f"[{i}/{len(sequence)}] Knocking port {port}...")
        if not send_knock(target, port, delay):
            print(f"❌ Failed to knock port {port}")
            return False
    
    print("")
    print("✅ Knock sequence completed!")
    print("   Waiting 1 second for server to process...")
    time.sleep(1)
    return True


def check_protected_port(target, protected_port, timeout=5.0):
    """Try connecting to the protected port after knocking"""
    print(f"")
    print(f"🔍 Checking if protected port {protected_port} is now open...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target, protected_port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {protected_port} is OPEN! You can now connect.")
            print(f"   Example: ssh user@{target} -p {protected_port}")
            return True
        else:
            print(f"❌ Port {protected_port} is still CLOSED")
            print(f"   Connection result: {result}")
            return False
    except Exception as e:
        print(f"❌ Error checking port: {e}")
        return False


def parse_args():
    parser = argparse.ArgumentParser(
        description="Port knocking client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 knock_client.py --target 172.20.0.40 --sequence 1234,5678,9012
  python3 knock_client.py --target 172.20.0.40 --sequence 1234,5678,9012 --check
        """
    )
    parser.add_argument("--target", required=True, help="Target host or IP")
    parser.add_argument(
        "--sequence",
        default=",".join(str(port) for port in DEFAULT_KNOCK_SEQUENCE),
        help="Comma-separated knock ports",
    )
    parser.add_argument(
        "--protected-port",
        type=int,
        default=DEFAULT_PROTECTED_PORT,
        help="Protected service port",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help="Delay between knocks in seconds",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Attempt connection to protected port after knocking",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        print("❌ Invalid sequence. Use comma-separated integers.")
        sys.exit(1)
    
    if len(sequence) < 2:
        print("❌ Sequence must have at least 2 ports")
        sys.exit(1)
    
    print("="*60)
    print("Port Knocking Client")
    print("="*60)
    print(f"Target: {args.target}")
    print(f"Sequence: {sequence}")
    print(f"Protected Port: {args.protected_port}")
    print("="*60)
    print("")
    
    # Perform knock sequence
    if perform_knock_sequence(args.target, sequence, args.delay):
        if args.check:
            check_protected_port(args.target, args.protected_port)
    else:
        print("❌ Knock sequence failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
