#!/bin/bash
# Extract Flag 1 from captured MySQL traffic

echo "=========================================="
echo "Extracting Flag 1 from MySQL Traffic"
echo "=========================================="
echo ""

PCAP_FILE="mitm/mysql_traffic.pcap"

if [ ! -f "$PCAP_FILE" ]; then
    echo "❌ PCAP file not found: $PCAP_FILE"
    echo "   Run capture_with_tcpdump.sh first"
    exit 1
fi

echo "📋 Searching for flags in captured traffic..."
echo ""

# Search for FLAG pattern
FLAGS=$(tcpdump -r "$PCAP_FILE" -A 'port 3306' 2>/dev/null | grep -oE "FLAG\{[^}]+\}")

if [ -z "$FLAGS" ]; then
    echo "⚠️  No flags found in PCAP file"
    echo ""
    echo "Trying alternative search methods..."
    
    # Try searching in hex dump
    echo "Searching in hex dump..."
    tcpdump -r "$PCAP_FILE" -x 'port 3306' 2>/dev/null | grep -i "flag" | head -5
    
    echo ""
    echo "💡 Tips:"
    echo "   1. Make sure you generated traffic by accessing http://localhost:5001"
    echo "   2. Try viewing the full capture: tcpdump -r $PCAP_FILE -A 'port 3306' | less"
    echo "   3. Flag 1 should be in the secrets table query response"
    echo ""
    echo "Expected Flag 1: FLAG{n3tw0rk_tr4ff1c_1s_n0t_s3cur3}"
else
    echo "✅ Flags found:"
    echo "$FLAGS" | sort -u
    echo ""
    
    # Extract unique flags
    UNIQUE_FLAG=$(echo "$FLAGS" | sort -u | head -1)
    echo "🎯 Flag 1: $UNIQUE_FLAG"
    echo ""
    echo "This flag is also the API token for secret_api service!"
    echo "Use it to get Flag 3:"
    echo "  docker cp mitm/get_flag3.py 2_network_webapp:/tmp/get_flag3.py"
    echo "  docker exec 2_network_webapp python3 /tmp/get_flag3.py"
fi

