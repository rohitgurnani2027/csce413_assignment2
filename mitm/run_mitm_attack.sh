#!/bin/bash
# Complete MITM attack workflow

echo "=========================================="
echo "Complete MITM Attack Workflow"
echo "=========================================="
echo ""

# Step 1: Capture traffic
echo "STEP 1: Capturing MySQL Traffic"
echo "----------------------------------------"
echo ""
echo "This will start capturing traffic. In another terminal:"
echo "  1. Open browser: http://localhost:5001"
echo "  2. Navigate through pages"
echo "  3. Refresh multiple times"
echo ""
read -p "Press Enter when ready to start capture (or Ctrl+C to cancel)..."

# Run capture - user will stop it manually
echo ""
echo "Starting capture..."
echo "⚠️  IMPORTANT: Keep this terminal open and press Ctrl+C when done capturing"
echo ""
echo "In another terminal or browser:"
echo "  1. Open: http://localhost:5001"
echo "  2. Navigate through pages"
echo "  3. Refresh multiple times"
echo ""
echo "Then come back here and press Ctrl+C to stop capture"
echo ""

# Run capture (user stops with Ctrl+C)
./mitm/capture_with_tcpdump.sh || {
    echo ""
    echo "Capture stopped"
}

echo ""
echo "STEP 2: Extracting Flag 1"
echo "----------------------------------------"
./mitm/extract_flag1.sh

echo ""
echo "STEP 3: Getting Flag 3"
echo "----------------------------------------"
./mitm/get_flag3.sh

echo ""
echo "=========================================="
echo "MITM Attack Complete!"
echo "=========================================="

