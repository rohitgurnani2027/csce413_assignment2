#!/bin/bash
# Script to interact with discovered services

echo "=========================================="
echo "Interacting with Discovered Services"
echo "=========================================="
echo ""

echo "1. Testing Secret API (172.20.0.21:8888)..."
echo "   [*] Root endpoint:"
docker exec 2_network_webapp python3 -c "
import urllib.request
try:
    with urllib.request.urlopen('http://172.20.0.21:8888/') as response:
        import json
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null || docker exec 2_network_webapp curl -s http://172.20.0.21:8888/
echo ""

echo "   [*] Health check:"
docker exec 2_network_webapp python3 -c "
import urllib.request
try:
    with urllib.request.urlopen('http://172.20.0.21:8888/health') as response:
        import json
        data = json.loads(response.read().decode())
        print(json.dumps(data, indent=2))
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null || docker exec 2_network_webapp curl -s http://172.20.0.21:8888/health
echo ""

echo "   [*] Flag endpoint (requires auth - will fail without token):"
docker exec 2_network_webapp python3 -c "
import urllib.request
try:
    req = urllib.request.Request('http://172.20.0.21:8888/flag')
    with urllib.request.urlopen(req) as response:
        print(response.read().decode())
except Exception as e:
    print(f'Error (expected): {e}')
" 2>/dev/null || docker exec 2_network_webapp curl -s http://172.20.0.21:8888/flag
echo ""
echo ""

echo "2. Testing Redis (172.20.0.22:6379)..."
docker exec 2_network_redis redis-cli -h 172.20.0.22 -p 6379 PING 2>/dev/null && echo "   ✅ Redis is responding" || echo "   ❌ Redis not responding"
echo ""

echo "3. SSH Service (172.20.0.20:2222)..."
echo "   To connect: docker exec -it 2_network_webapp bash"
echo "   Then: ssh sshuser@172.20.0.20 -p 2222"
echo "   Password: SecurePass2024!"
echo ""

echo "=========================================="
echo "Summary of Discovered Services"
echo "=========================================="
echo ""
echo "✅ webapp:        172.20.0.10:5000  (Flask)"
echo "✅ secret_ssh:    172.20.0.20:2222  (SSH - Flag 2 here)"
echo "✅ secret_api:    172.20.0.21:8888  (REST API - Flag 3 here, needs Flag 1)"
echo "✅ redis:         172.20.0.22:6379  (Redis)"
echo "✅ database:      172.20.0.11:3306  (MySQL - Flag 1 in traffic)"
echo ""

