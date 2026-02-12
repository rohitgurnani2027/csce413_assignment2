#!/usr/bin/env python3
"""
SSH Honeypot
Simulates SSH service and logs all connection attempts and interactions
"""

import socket
import threading
import time
from datetime import datetime

from logger import (
    setup_logging,
    log_connection_start,
    log_connection_end,
    log_authentication_attempt,
    log_command,
    get_statistics
)

# SSH banner (realistic OpenSSH banner)
SSH_BANNER = "SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.13\r\n"
HONEYPOT_PORT = 22
MAX_CONNECTIONS = 10

# Fake credentials (honeypot accepts any, but logs everything)
FAKE_USERS = ["admin", "root", "user", "test", "guest"]


class SSHConnection:
    """Handles a single SSH connection"""
    
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.source_ip = addr[0]
        self.source_port = addr[1]
        self.start_time = datetime.now()
        self.authenticated = False
        self.username = None
        
    def handle(self):
        """Handle the SSH connection - log everything"""
        try:
            log_connection_start(self.source_ip, self.source_port)
            
            # Send the SSH banner to make it look real
            self.conn.send(SSH_BANNER.encode())
            
            # Client will send its banner back, we can ignore it
            try:
                self.conn.recv(1024)
            except:
                pass
            
            # Do the SSH handshake
            self.conn.send(b"SSH-2.0-OpenSSH_8.9p1\r\n")
            
            # Give them a moment to try to authenticate
            time.sleep(0.5)
            
            # Try to read any authentication data they send
            try:
                self.conn.settimeout(5.0)
                data = self.conn.recv(4096)
                
                if data:
                    # Try to parse what they sent (this is simplified)
                    data_str = data.decode('utf-8', errors='ignore')
                    
                    # Look for password/auth attempts
                    if "password" in data_str.lower() or "auth" in data_str.lower():
                        username = self.extract_username(data_str)
                        password = self.extract_password(data_str) or "***"
                        
                        # Log the attempt (always fail since it's a honeypot)
                        log_authentication_attempt(
                            self.source_ip,
                            self.source_port,
                            username,
                            password,
                            success=False
                        )
                        
                        # Send back auth failure
                        self.conn.send(b"\x00\x00\x00\x0c\x00\x00\x00\x05\x00\x00\x00\x00")
                        
                        # Wait a bit to see if they try anything else
                        time.sleep(2)
                        
                        # Try to catch any commands they might send
                        try:
                            self.conn.settimeout(2.0)
                            more_data = self.conn.recv(4096)
                            if more_data:
                                cmd = more_data.decode('utf-8', errors='ignore')[:100]
                                log_command(self.source_ip, self.source_port, cmd)
                        except:
                            pass
            except socket.timeout:
                # They didn't send anything, that's fine
                pass
            except Exception:
                # Something went wrong, just continue
                pass
            
        except Exception:
            # Connection error or something, log it and move on
            pass
        finally:
            # Always log when connection ends
            duration = (datetime.now() - self.start_time).total_seconds()
            log_connection_end(self.source_ip, self.source_port, duration)
            self.conn.close()
    
    def extract_username(self, data):
        """Try to extract username from the data (not perfect but works for most cases)"""
        # Check if any of our known fake usernames appear
        for user in FAKE_USERS:
            if user.lower() in data.lower():
                return user
        
        # Otherwise try to find something that looks like a username
        words = data.split()
        for word in words:
            if len(word) > 2 and word.isalnum():
                return word
        
        return "unknown"
    
    def extract_password(self, data):
        """Extract password from SSH data (simplified)"""
        # Look for common password patterns
        common_passwords = ["password", "123456", "admin", "root", "test"]
        data_lower = data.lower()
        
        for pwd in common_passwords:
            if pwd in data_lower:
                return pwd
        
        return None


def run_honeypot():
    """Run the SSH honeypot server"""
    setup_logging()
    logger = logging.getLogger("Honeypot")
    
    logger.info("="*60)
    logger.info("SSH Honeypot Starting")
    logger.info("="*60)
    logger.info(f"Listening on port {HONEYPOT_PORT}")
    logger.info(f"Logging to: /app/logs/")
    logger.info("="*60)
    logger.info("")
    
    # Create socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('0.0.0.0', HONEYPOT_PORT))
        server_socket.listen(MAX_CONNECTIONS)
        logger.info(f"✅ Honeypot listening on port {HONEYPOT_PORT}")
        logger.info("")
        
        while True:
            try:
                conn, addr = server_socket.accept()
                logger.info(f"🔔 New connection from {addr[0]}:{addr[1]}")
                
                # Handle connection in separate thread
                connection = SSHConnection(conn, addr)
                thread = threading.Thread(target=connection.handle, daemon=True)
                thread.start()
                
            except Exception as e:
                logger.error(f"Error accepting connection: {e}")
                
    except OSError as e:
        logger.error(f"Failed to bind to port {HONEYPOT_PORT}: {e}")
        logger.error("Make sure port 22 is available or change HONEYPOT_PORT")
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down honeypot...")
        stats = get_statistics()
        logger.info(f"📊 Statistics: {stats}")
        logger.info("✅ Honeypot stopped")
    finally:
        server_socket.close()


if __name__ == "__main__":
    import logging
    run_honeypot()
