# Port Scanner

A comprehensive port scanning tool for network reconnaissance.

## Features

- **TCP Connect Scanning**: Reliable port detection
- **Multi-threading**: Fast parallel scanning with configurable thread count
- **Banner Grabbing**: Automatically detects service banners
- **Service Identification**: Identifies common services by port and banner
- **CIDR Support**: Scan entire subnets (e.g., 172.20.0.0/24)
- **Progress Indicators**: Real-time scan progress
- **JSON Output**: Export results to JSON format
- **Error Handling**: Graceful handling of timeouts and connection errors

## Usage

### Basic Usage

```bash
# Scan a single host
python3 -m port_scanner --target 172.20.0.10 --ports 1-1000

# Scan a specific port
python3 -m port_scanner --target 172.20.0.10 --ports 3306

# Scan entire subnet
python3 -m port_scanner --target 172.20.0.0/24 --ports 1-10000 --threads 200
```

### Advanced Options

```bash
# Custom thread count and timeout
python3 -m port_scanner --target webapp --ports 1-65535 --threads 200 --timeout 2.0

# Disable banner grabbing (faster)
python3 -m port_scanner --target 172.20.0.10 --ports 1-1000 --no-banner

# Save results to JSON
python3 -m port_scanner --target 172.20.0.10 --ports 1-10000 --json results.json

# Quiet mode (minimal output)
python3 -m port_scanner --target 172.20.0.10 --ports 1-1000 --quiet
```

## Examples

### Scan Docker Network

```bash
# Scan all hosts in the Docker network
python3 -m port_scanner --target 172.20.0.0/24 --ports 1-10000 --threads 100
```

### Scan Specific Service

```bash
# Scan for web services
python3 -m port_scanner --target 172.20.0.10 --ports 80,443,8000-9000
```

## Output Format

The scanner displays results in real-time:
```
[+] Port  3306 is OPEN - MySQL - 5.7.44-log
[+] Port  5000 is OPEN - Flask/Development
[+] Port  6379 is OPEN - Redis
```

JSON output format:
```json
{
  "172.20.0.10": [
    {
      "port": 3306,
      "state": "open",
      "service": "MySQL",
      "banner": "5.7.44-log"
    }
  ]
}
```

## Implementation Details

- Uses Python's `socket` module for TCP connections
- Implements `ThreadPoolExecutor` for concurrent scanning
- Banner grabbing attempts to read initial response (first 1024 bytes)
- Service identification uses both port number and banner analysis
- Timeout handling prevents hanging on filtered ports

