#!/bin/bash
# Run the port scanner from inside the Docker network
# This allows access to all container IPs (172.20.0.x)

echo "=========================================="
echo "Running Port Scanner from Docker Network"
echo "=========================================="
echo ""

# Check if containers are running
if ! docker compose ps | grep -q "Up"; then
    echo "❌ Containers are not running. Starting them..."
    docker compose up -d
    echo "Waiting 10 seconds for services to start..."
    sleep 10
fi

echo "📋 Testing connectivity first..."
echo ""

# Quick connectivity test
docker exec 2_network_webapp python3 -c "
import socket
targets = [
    ('172.20.0.10', 5000, 'webapp'),
    ('172.20.0.20', 2222, 'secret_ssh'),
    ('172.20.0.21', 8888, 'secret_api'),
    ('172.20.0.22', 6379, 'redis'),
]
print('[*] Quick connectivity test:')
for ip, port, name in targets:
    s = socket.socket()
    s.settimeout(1)
    result = s.connect_ex((ip, port))
    s.close()
    status = '✅ OPEN' if result == 0 else '❌ CLOSED'
    print(f'   {name:15} {ip}:{port:5d} - {status}')
"

echo ""
echo "=========================================="
echo "Running full port scanner..."
echo "=========================================="
echo ""

# Copy scanner into container and run
echo "📦 Copying scanner into container..."
docker cp port_scanner/main.py 2_network_webapp:/tmp/scanner.py

echo ""
echo "🔍 Scanning webapp (172.20.0.10:5000-5010)..."
docker exec 2_network_webapp python3 /tmp/scanner.py --target 172.20.0.10 --ports 5000-5010 --threads 10

echo ""
echo "🔍 Scanning secret_ssh (172.20.0.20:2000-3000)..."
docker exec 2_network_webapp python3 /tmp/scanner.py --target 172.20.0.20 --ports 2000-3000 --threads 50

echo ""
echo "🔍 Scanning secret_api (172.20.0.21:8000-9000)..."
docker exec 2_network_webapp python3 /tmp/scanner.py --target 172.20.0.21 --ports 8000-9000 --threads 50

echo ""
echo "🔍 Scanning redis (172.20.0.22:6000-7000)..."
docker exec 2_network_webapp python3 /tmp/scanner.py --target 172.20.0.22 --ports 6000-7000 --threads 50

echo ""
echo "✅ Scanning complete!"

