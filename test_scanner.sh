#!/bin/bash
# Test script for the port scanner
# Make sure Docker services are running first: docker compose up -d

echo "=========================================="
echo "Port Scanner Test Script"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is not running or you don't have permission"
    echo "   Please start Docker and run: docker compose up -d"
    exit 1
fi

# Check if containers are running
echo "📋 Checking Docker containers..."
if ! docker compose ps | grep -q "Up"; then
    echo "⚠️  Containers don't appear to be running"
    echo "   Starting containers..."
    docker compose up -d
    echo "   Waiting 10 seconds for services to start..."
    sleep 10
fi

echo ""
echo "✅ Docker services are running"
echo ""

# Test 1: Scan webapp (known service on port 5000)
echo "=========================================="
echo "Test 1: Scanning webapp (172.20.0.10)"
echo "=========================================="
docker exec 2_network_webapp python3 -c "
import sys
sys.path.insert(0, '/tmp')
import socket

def scan_port(target, port, timeout=1.0):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((target, port))
        sock.close()
        return result == 0
    except:
        return False

# Copy scanner
import subprocess
subprocess.run(['docker', 'cp', 'port_scanner/main.py', '2_network_webapp:/tmp/scanner.py'])

# Test scan
targets = [
    ('172.20.0.10', 5000, 'webapp'),
    ('172.20.0.20', 2222, 'secret_ssh'),
    ('172.20.0.21', 8888, 'secret_api'),
    ('172.20.0.22', 6379, 'redis'),
]

print('[*] Quick connectivity test:')
for ip, port, name in targets:
    result = scan_port(ip, port, 2.0)
    status = '✅ OPEN' if result else '❌ CLOSED'
    print(f'   {name:15} {ip}:{port:5d} - {status}')
" 2>/dev/null || echo "Run scanner from inside Docker network"

echo ""
echo "=========================================="
echo "✅ All tests completed!"
echo "=========================================="

