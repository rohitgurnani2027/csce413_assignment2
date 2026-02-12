## MITM Attack Tools

Complete tools for performing man-in-the-middle attack on MySQL traffic.

### Files

- `capture_traffic.py` - Python script using scapy to capture and analyze traffic
- `capture_with_tcpdump.sh` - Shell script using tcpdump to capture traffic
- `extract_flag1.sh` - Extract Flag 1 from captured traffic
- `get_flag3.sh` - Use Flag 1 to get Flag 3 from API
- `run_mitm_attack.sh` - Complete automated workflow

### Quick Start

```bash
# Option 1: Automated workflow
./mitm/run_mitm_attack.sh

# Option 2: Step by step
# 1. Capture traffic
./mitm/capture_with_tcpdump.sh

# 2. Extract Flag 1
./mitm/extract_flag1.sh

# 3. Get Flag 3
./mitm/get_flag3.sh
```

### Requirements

- Docker containers running
- sudo access (for packet capture)
- tcpdump or scapy installed
- Network access to Docker bridge

### See PART2_GUIDE.md for detailed instructions
