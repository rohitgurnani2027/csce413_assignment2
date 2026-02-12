"""Logging functionality for the honeypot."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("/app/logs")
LOG_FILE = LOG_DIR / "connections.jsonl"
HONEYPOT_LOG = LOG_DIR / "honeypot.log"


def setup_logging():
    """Setup logging directories and files"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Setup Python logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(HONEYPOT_LOG),
            logging.StreamHandler()
        ]
    )


def log_connection(source_ip, source_port, event_type, **kwargs):
    """Log a connection event to JSONL file"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "source_ip": source_ip,
        "source_port": source_port,
        "event_type": event_type,
        **kwargs
    }
    
    # Write to JSONL file
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    # Also log to standard logger
    logger = logging.getLogger("Honeypot")
    logger.info(f"{event_type.upper()}: {source_ip}:{source_port} - {kwargs.get('message', '')}")


def log_authentication_attempt(source_ip, source_port, username, password, success=False):
    """Log an authentication attempt"""
    log_connection(
        source_ip=source_ip,
        source_port=source_port,
        event_type="authentication_attempt",
        username=username,
        password=password,
        success=success,
        message=f"Login attempt: {username} / {'*' * len(password)}"
    )


def log_command(source_ip, source_port, command, output=None):
    """Log a command execution"""
    log_connection(
        source_ip=source_ip,
        source_port=source_port,
        event_type="command_executed",
        command=command,
        output=output,
        message=f"Command: {command}"
    )


def log_connection_start(source_ip, source_port):
    """Log connection start"""
    log_connection(
        source_ip=source_ip,
        source_port=source_port,
        event_type="connection_start",
        message="New connection established"
    )


def log_connection_end(source_ip, source_port, duration_seconds):
    """Log connection end"""
    log_connection(
        source_ip=source_ip,
        source_port=source_port,
        event_type="connection_end",
        duration_seconds=duration_seconds,
        message=f"Connection closed after {duration_seconds:.2f} seconds"
    )


def get_logs():
    """Read all logs from JSONL file"""
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


def get_statistics():
    """Get statistics from logs"""
    logs = get_logs()
    
    if not logs:
        return {
            "total_connections": 0,
            "unique_ips": 0,
            "authentication_attempts": 0,
            "failed_logins": 0,
            "successful_logins": 0,
            "commands_executed": 0
        }
    
    unique_ips = set(log.get("source_ip") for log in logs)
    auth_attempts = [log for log in logs if log.get("event_type") == "authentication_attempt"]
    failed_logins = [log for log in auth_attempts if not log.get("success", False)]
    successful_logins = [log for log in auth_attempts if log.get("success", False)]
    commands = [log for log in logs if log.get("event_type") == "command_executed"]
    
    return {
        "total_connections": len(logs),
        "unique_ips": len(unique_ips),
        "authentication_attempts": len(auth_attempts),
        "failed_logins": len(failed_logins),
        "successful_logins": len(successful_logins),
        "commands_executed": len(commands)
    }
