# Port Knocking Implementation

## Overview

Port knocking is a security mechanism that keeps a port closed until a client sends a specific sequence of connection attempts to predefined ports. Only after the correct "knock sequence" is received does the firewall open the protected port.

## Implementation

### Design Decisions

- **Protected Service**: SSH server on port 2222 (secret_ssh)
- **Knock Sequence**: 1234, 5678, 9012 (configurable)
- **Protocol**: TCP knocks (connection attempts)
- **Timing Window**: 10 seconds (sequence must complete within this time)
- **Port Timeout**: 60 seconds (port closes automatically after opening)

### Architecture

**Server (`knock_server.py`):**
- Listens on each knock port in the sequence
- Tracks knock attempts per source IP
- Validates sequence order and timing
- Opens protected port using iptables when sequence is correct
- Automatically closes port after timeout

**Client (`knock_client.py`):**
- Sends connection attempts to each port in sequence
- Waits for server to process
- Optionally checks if protected port is now open

### Features

- ✅ Multi-threaded server (handles multiple clients)
- ✅ Per-IP tracking (each IP has its own sequence state)
- ✅ Timing constraints (sequence must complete within window)
- ✅ Automatic port closure (timeout-based)
- ✅ Sequence validation (wrong port resets sequence)
- ✅ iptables integration (dynamic firewall rules)

## Usage

### Starting the Server

```bash
# From inside container or host
python3 knock_server.py

# With custom sequence
python3 knock_server.py --sequence 1111,2222,3333 --protected-port 2222

# With custom timing
python3 knock_server.py --window 5.0 --timeout 30.0
```

### Using the Client

```bash
# Basic usage
python3 knock_client.py --target 172.20.0.40 --sequence 1234,5678,9012

# With port check
python3 knock_client.py --target 172.20.0.40 --sequence 1234,5678,9012 --check

# Custom delay between knocks
python3 knock_client.py --target 172.20.0.40 --sequence 1234,5678,9012 --delay 0.5
```

### Demo Script

```bash
./demo.sh [target_ip] [sequence] [protected_port]

# Example
./demo.sh 172.20.0.40 "1234,5678,9012" 2222
```

## Testing

### Before Knocking

```bash
# Should fail - port is closed
ssh sshuser@172.20.0.40 -p 2222
# Connection refused
```

### After Knocking

```bash
# Perform knock sequence
python3 knock_client.py --target 172.20.0.40 --sequence 1234,5678,9012 --check

# Now should succeed
ssh sshuser@172.20.0.40 -p 2222
# Connection successful
```

## Security Analysis

### Strengths

- ✅ Hides service from port scanners
- ✅ Reduces attack surface
- ✅ Simple to implement
- ✅ Low overhead

### Limitations

- ⚠️ Security through obscurity (not true security)
- ⚠️ Vulnerable to traffic analysis
- ⚠️ Sequence can be intercepted and replayed
- ⚠️ No authentication (anyone with sequence can access)
- ⚠️ Timing analysis can reveal sequence

### Improvements

- Add timing constraints (sequence must complete within X seconds) ✅
- Implement sequence randomization per client
- Add authentication after port opening
- Use encrypted knock sequences
- Implement rate limiting
- Add IP whitelisting

## Files

- `knock_server.py` - Server implementation
- `knock_client.py` - Client implementation
- `Dockerfile` - Container setup
- `demo.sh` - Demonstration script
- `README.md` - This file

## Docker

The port knocking server runs in a Docker container with:
- NET_ADMIN capability (required for iptables)
- Access to vulnerable_network
- IP: 172.20.0.40

To run:
```bash
docker compose up port_knocking
```
