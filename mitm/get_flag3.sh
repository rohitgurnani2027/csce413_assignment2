#!/bin/bash
# Use Flag 1 to get Flag 3 from secret_api

echo "=========================================="
echo "Getting Flag 3 from Secret API"
echo "=========================================="
echo ""

# Use Python script (works in containers without curl)
docker cp mitm/get_flag3.py 2_network_webapp:/tmp/get_flag3.py 2>/dev/null
docker exec 2_network_webapp python3 /tmp/get_flag3.py

