#!/usr/bin/env bash
# Port Knocking Demo Script

set -euo pipefail

TARGET_IP=${1:-172.20.0.40}
SEQUENCE=${2:-"1234,5678,9012"}
PROTECTED_PORT=${3:-2222}

echo "=========================================="
echo "Port Knocking Demo"
echo "=========================================="
echo "Target: $TARGET_IP"
echo "Sequence: $SEQUENCE"
echo "Protected Port: $PROTECTED_PORT"
echo "=========================================="
echo ""

echo "[1/3] Testing protected port BEFORE knocking..."
if command -v nc >/dev/null 2>&1; then
    nc -z -v "$TARGET_IP" "$PROTECTED_PORT" 2>&1 || echo "   ✅ Port is closed (expected)"
else
    python3 -c "
import socket
s = socket.socket()
s.settimeout(1)
result = s.connect_ex(('$TARGET_IP', $PROTECTED_PORT))
s.close()
if result == 0:
    print('   ❌ Port is OPEN (unexpected)')
else:
    print('   ✅ Port is closed (expected)')
"
fi
echo ""

echo "[2/3] Sending knock sequence..."
python3 knock_client.py --target "$TARGET_IP" --sequence "$SEQUENCE" --check
echo ""

echo "[3/3] Testing protected port AFTER knocking..."
if command -v nc >/dev/null 2>&1; then
    nc -z -v "$TARGET_IP" "$PROTECTED_PORT" 2>&1 && echo "   ✅ Port is now OPEN!" || echo "   ❌ Port is still closed"
else
    python3 -c "
import socket
s = socket.socket()
s.settimeout(2)
result = s.connect_ex(('$TARGET_IP', $PROTECTED_PORT))
s.close()
if result == 0:
    print('   ✅ Port is now OPEN!')
else:
    print('   ❌ Port is still closed')
"
fi
echo ""

echo "=========================================="
echo "Demo Complete!"
echo "=========================================="

