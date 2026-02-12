# SSH Honeypot Implementation

## Overview

A honeypot is a security mechanism that creates a decoy system to attract and detect attackers. This SSH honeypot simulates a real SSH service and logs all connection attempts, authentication attempts, and interactions for analysis.

## Implementation

### Design Decisions

- **Service Type**: SSH honeypot (simulates OpenSSH)
- **Port**: 22 (standard SSH port)
- **Banner**: Realistic OpenSSH banner
- **Authentication**: Always fails (logs all attempts)
- **Logging**: JSONL format (one entry per line)

### Architecture

**Main Components:**

1. **Honeypot Server (`honeypot.py`):**
   - Listens on port 22
   - Accepts SSH connections
   - Simulates SSH protocol
   - Logs all interactions

2. **Logger (`logger.py`):**
   - Structured logging to JSONL
   - Logs connection events
   - Logs authentication attempts
   - Logs commands executed
   - Provides statistics

3. **Log Analyzer (`analyze_logs.py`):**
   - Analyzes captured logs
   - Generates statistics
   - Identifies attack patterns
   - Creates analysis report

### Features

- ✅ Realistic SSH banner
- ✅ Connection logging
- ✅ Authentication attempt logging (usernames/passwords)
- ✅ Command logging
- ✅ Multi-threaded (handles multiple connections)
- ✅ Statistics generation
- ✅ Attack pattern detection

## Usage

### Starting the Honeypot

```bash
# From Docker
docker compose up honeypot

# Or manually
python3 honeypot.py
```

### Simulating Attacks

```bash
# Try to connect
ssh admin@localhost -p 2222

# Try different usernames/passwords
ssh root@localhost -p 2222
ssh test@localhost -p 2222

# Try commands (if connection succeeds)
# (honeypot will log everything)
```

### Viewing Logs

```bash
# View connection logs
cat honeypot/logs/connections.jsonl

# View honeypot log
cat honeypot/logs/honeypot.log

# Analyze logs
docker exec 2_network_honeypot python3 analyze_logs.py
```

## Log Format

### Connection Start
```json
{
  "timestamp": "2024-01-15T10:30:00.123456",
  "source_ip": "172.20.0.50",
  "source_port": 54321,
  "event_type": "connection_start",
  "message": "New connection established"
}
```

### Authentication Attempt
```json
{
  "timestamp": "2024-01-15T10:30:05.123456",
  "source_ip": "172.20.0.50",
  "source_port": 54321,
  "event_type": "authentication_attempt",
  "username": "admin",
  "password": "password123",
  "success": false,
  "message": "Login attempt: admin / ************"
}
```

### Command Executed
```json
{
  "timestamp": "2024-01-15T10:30:10.123456",
  "source_ip": "172.20.0.50",
  "source_port": 54321,
  "event_type": "command_executed",
  "command": "ls -la",
  "message": "Command: ls -la"
}
```

## Analysis

### Statistics Generated

- Total connections
- Unique IP addresses
- Authentication attempts
- Failed vs successful logins
- Commands executed
- Top usernames/passwords
- Attack patterns

### Attack Patterns Detected

- **Brute Force**: Multiple failed attempts from same IP
- **Credential Stuffing**: Known username/password pairs
- **Reconnaissance**: Port scanning, banner grabbing
- **Command Injection**: Malicious commands attempted

## Files

- `honeypot.py` - Main honeypot implementation
- `logger.py` - Logging functionality
- `analyze_logs.py` - Log analysis tool
- `analysis.md` - Analysis report template
- `Dockerfile` - Container setup
- `README.md` - This file

## Docker

The honeypot runs in a Docker container:
- Exposes port 22 (mapped to host port 2222)
- Logs stored in `honeypot/logs/`
- IP: 172.20.0.30

To run:
```bash
docker compose up honeypot
```

## Security Considerations

### Legal and Ethical

- ✅ Only deployed in controlled environment
- ✅ Used for educational purposes
- ⚠️ In production, ensure legal compliance
- ⚠️ Consider data privacy regulations

### Best Practices

- Store logs securely
- Rotate logs regularly
- Monitor honeypot health
- Integrate with alerting systems
- Use honeypots as part of defense in depth
