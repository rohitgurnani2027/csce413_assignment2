#!/usr/bin/env python3
"""
Port Knocking Server
Listens for knock sequence and opens protected port using iptables
"""

import argparse
import logging
import socket
import subprocess
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta

DEFAULT_KNOCK_SEQUENCE = [1234, 5678, 9012]
DEFAULT_PROTECTED_PORT = 2222
DEFAULT_SEQUENCE_WINDOW = 10.0
DEFAULT_PORT_TIMEOUT = 60.0  # Port stays open for 60 seconds


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def run_iptables_command(command):
    """Execute iptables command"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"iptables command failed: {e.stderr}")
        return False, e.stderr


def open_protected_port(protected_port, source_ip):
    """Open the protected port using iptables"""
    # Add a rule to allow this specific IP to access the protected port
    command = f"iptables -I INPUT 1 -s {source_ip} -p tcp --dport {protected_port} -j ACCEPT"
    success, output = run_iptables_command(command)
    
    if success:
        logging.info(f"✅ Opened port {protected_port} for {source_ip}")
        return True
    else:
        logging.error(f"❌ Failed to open port {protected_port} for {source_ip}")
        return False


def close_protected_port(protected_port, source_ip):
    """Close the protected port using iptables"""
    # Remove the rule allowing traffic from specific IP
    command = f"iptables -D INPUT -s {source_ip} -p tcp --dport {protected_port} -j ACCEPT"
    success, output = run_iptables_command(command)
    
    if success:
        logging.info(f"🔒 Closed port {protected_port} for {source_ip}")
    else:
        logging.warning(f"⚠️  Could not remove rule for {source_ip} (may not exist)")
    
    return success


def initialize_firewall(protected_port):
    """Initialize firewall - block protected port by default"""
    # Drop all traffic to protected port (will be overridden by ACCEPT rules)
    command = f"iptables -I INPUT 1 -p tcp --dport {protected_port} -j DROP"
    success, output = run_iptables_command(command)
    
    if success:
        logging.info(f"🔒 Protected port {protected_port} is now blocked by default")
    else:
        logging.warning(f"⚠️  Could not set default DROP rule (may already exist)")
    
    return success


class KnockTracker:
    """Tracks knock sequences per source IP"""
    
    def __init__(self, sequence, window_seconds, protected_port, port_timeout):
        self.sequence = sequence
        self.window_seconds = window_seconds
        self.protected_port = protected_port
        self.port_timeout = port_timeout
        self.progress = defaultdict(list)  # IP -> list of (port, timestamp)
        self.open_ports = {}  # IP -> (opened_at, thread)
        self.lock = threading.Lock()
    
    def record_knock(self, source_ip, port):
        """Record a knock from source IP and check if sequence is complete"""
        with self.lock:
            now = datetime.now()
            
            # Remove old knocks that are outside the time window
            cutoff = now - timedelta(seconds=self.window_seconds)
            self.progress[source_ip] = [
                (p, ts) for p, ts in self.progress[source_ip]
                if ts > cutoff
            ]
            
            # Add this new knock
            self.progress[source_ip].append((port, now))
            
            # See if they got the sequence right
            if self.check_sequence(source_ip):
                logging.info(f"🎯 Correct sequence received from {source_ip}!")
                self.open_port_for_ip(source_ip)
                # Clear the progress since we're done
                self.progress[source_ip] = []
            else:
                # Check if they hit the wrong port - if so, reset
                expected_port = self.sequence[len(self.progress[source_ip]) - 1]
                if port != expected_port:
                    logging.warning(f"❌ Wrong port {port} from {source_ip} (expected {expected_port}). Resetting sequence.")
                    self.progress[source_ip] = []
    
    def check_sequence(self, source_ip):
        """Check if source IP has completed the knock sequence"""
        knocks = [p for p, ts in self.progress[source_ip]]
        
        if len(knocks) != len(self.sequence):
            return False
        
        return knocks == self.sequence
    
    def open_port_for_ip(self, source_ip):
        """Open protected port for source IP"""
        # Close if already open
        if source_ip in self.open_ports:
            self.close_port_for_ip(source_ip)
        
        # Open port
        if open_protected_port(self.protected_port, source_ip):
            opened_at = datetime.now()
            
            # Schedule automatic closure
            def close_after_timeout():
                time.sleep(self.port_timeout)
                self.close_port_for_ip(source_ip)
            
            thread = threading.Thread(target=close_after_timeout, daemon=True)
            thread.start()
            
            self.open_ports[source_ip] = (opened_at, thread)
            logging.info(f"⏰ Port {self.protected_port} will close for {source_ip} after {self.port_timeout} seconds")
    
    def close_port_for_ip(self, source_ip):
        """Close protected port for source IP"""
        if source_ip in self.open_ports:
            close_protected_port(self.protected_port, source_ip)
            del self.open_ports[source_ip]


def listen_for_knocks(sequence, window_seconds, protected_port, port_timeout):
    """Listen for knock sequence and open the protected port"""
    logger = logging.getLogger("KnockServer")
    logger.info("="*60)
    logger.info("Port Knocking Server Starting")
    logger.info("="*60)
    logger.info(f"Knock sequence: {sequence}")
    logger.info(f"Protected port: {protected_port}")
    logger.info(f"Sequence window: {window_seconds} seconds")
    logger.info(f"Port timeout: {port_timeout} seconds")
    logger.info("="*60)
    
    # Initialize firewall
    initialize_firewall(protected_port)
    
    # Create tracker
    tracker = KnockTracker(sequence, window_seconds, protected_port, port_timeout)
    
    # Create sockets for each knock port
    sockets = []
    for port in sequence:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('0.0.0.0', port))
            sock.listen(5)
            sockets.append((sock, port))
            logger.info(f"👂 Listening on knock port {port}")
        except OSError as e:
            logger.error(f"❌ Failed to bind to port {port}: {e}")
            return
    
    logger.info("✅ All knock ports listening. Waiting for sequence...")
    logger.info("")
    
    # Accept connections on all ports
    def handle_connection(sock, port):
        while True:
            try:
                conn, addr = sock.accept()
                source_ip = addr[0]
                logger.info(f"🔔 Knock received: port {port} from {source_ip}")
                
                # Record knock
                tracker.record_knock(source_ip, port)
                
                # Close connection immediately (we just needed the connection attempt)
                conn.close()
            except Exception as e:
                logger.error(f"Error handling connection on port {port}: {e}")
    
    # Start threads for each knock port
    threads = []
    for sock, port in sockets:
        thread = threading.Thread(target=handle_connection, args=(sock, port), daemon=True)
        thread.start()
        threads.append(thread)
    
    # Keep server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down port knocking server...")
        for sock, port in sockets:
            sock.close()
        logger.info("✅ Server stopped")


def parse_args():
    parser = argparse.ArgumentParser(description="Port knocking server")
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
        "--window",
        type=float,
        default=DEFAULT_SEQUENCE_WINDOW,
        help="Seconds allowed to complete the sequence",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_PORT_TIMEOUT,
        help="Seconds before port closes automatically",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging()
    
    try:
        sequence = [int(port) for port in args.sequence.split(",")]
    except ValueError:
        raise SystemExit("Invalid sequence. Use comma-separated integers.")
    
    if len(sequence) < 2:
        raise SystemExit("Sequence must have at least 2 ports")
    
    listen_for_knocks(sequence, args.window, args.protected_port, args.timeout)


if __name__ == "__main__":
    main()
