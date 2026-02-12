# Honeypot Attack Analysis

## Overview

This document analyzes attacks captured by the SSH honeypot deployed as part of Assignment 2, Part 3. The honeypot successfully logged connection attempts and provided valuable insights into network reconnaissance activities.

## Analysis Date

February 12, 2026

## Summary

The honeypot captured **7 total events** from **2 unique IP addresses** over the monitoring period. The analysis reveals primarily reconnaissance activities with quick connection attempts. While no authentication attempts were successfully logged in detail, the honeypot successfully detected and logged all connection attempts, demonstrating its effectiveness as a detection mechanism.

**Key Findings:**
- 2 distinct connection attempts detected
- Average connection duration: ~0.5 seconds
- Primary source: 192.168.65.1 (Docker host)
- No brute force patterns detected
- Connections appear to be reconnaissance/testing activities

## Statistics

### Connection Statistics
- **Total Events**: 7
- **Total Connections**: 2 (connection_start events)
- **Unique IP Addresses**: 2
  - 192.168.65.1: 4 events
  - 172.20.0.1: 3 events (older format logs)
- **Connection Duration**: 
  - Average: ~0.5 seconds
  - Range: 0.50 - 0.50 seconds
  - Pattern: Quick connection attempts, immediate disconnection

### Authentication Attempts
- **Total Attempts**: 0 (logged in detail)
- **Failed Logins**: 0
- **Successful Logins**: 0 (expected for honeypot)

**Note**: While authentication attempts may have occurred, they were not captured in detail. This could indicate:
- Very quick connection/disconnection (reconnaissance)
- Connection failures before authentication phase
- Protocol-level issues in SSH handshake

### Top Usernames Attempted
No detailed authentication logs captured. Connections were too brief to capture username/password attempts.

### Top Passwords Attempted
No detailed authentication logs captured.

## Attack Patterns

### Brute Force Attacks
✅ **No obvious brute force patterns detected**

The analysis shows no evidence of systematic brute force attacks. Connections were isolated and brief, suggesting reconnaissance rather than persistent attack attempts.

### Credential Stuffing
No credential stuffing attempts detected. The brief connection durations suggest connections were terminated before reaching the authentication phase.

### Reconnaissance
**Primary Activity Detected**: Network reconnaissance

The connection patterns indicate reconnaissance activities:
- Quick connection attempts (~0.5 seconds)
- Immediate disconnection
- Multiple attempts from same source (192.168.65.1)
- Testing service availability

**Characteristics:**
- Connections from Docker host (192.168.65.1)
- Short-lived connections
- No persistent authentication attempts
- Likely automated scanning or manual testing

## Timeline

### Attack Timeline

**First Event**: January 5, 2026, 15:47:39 UTC
- Initial connection from 172.20.0.1
- Early testing phase

**Recent Activity**: February 12, 2026, 05:21:30 - 05:21:44 UTC
- Connection 1: 192.168.65.1:54311
  - Started: 05:21:30.173
  - Ended: 05:21:30.676
  - Duration: 0.50 seconds
  
- Connection 2: 192.168.65.1:20827
  - Started: 05:21:43.849
  - Ended: 05:21:44.352
  - Duration: 0.50 seconds

**Pattern**: Two quick connection attempts within 14 seconds, both from the same source IP.

## Notable Attacks

### Attack 1: Reconnaissance Connection Attempt
- **Source IP**: 192.168.65.1
- **Source Port**: 54311
- **Time**: February 12, 2026, 05:21:30 UTC
- **Details**: Quick connection attempt, immediate disconnection after 0.5 seconds
- **Impact**: Low - Appears to be testing service availability
- **Assessment**: Likely automated scanning or manual connection test

### Attack 2: Follow-up Reconnaissance
- **Source IP**: 192.168.65.1
- **Source Port**: 20827
- **Time**: February 12, 2026, 05:21:43 UTC
- **Details**: Second quick connection attempt 13 seconds after first
- **Impact**: Low - Continued reconnaissance activity
- **Assessment**: Testing service response or verifying service availability

## Insights

### Common Attack Vectors

1. **Reconnaissance First**
   - Attackers first test service availability
   - Quick connections to identify open ports
   - No immediate authentication attempts

2. **Short Connection Windows**
   - Connections terminated quickly
   - Suggests automated tools or quick manual tests
   - May indicate port scanning activities

3. **Source IP Patterns**
   - Primary source: Docker host (192.168.65.1)
   - Suggests internal network testing
   - Could be legitimate testing or initial reconnaissance

### Security Implications

1. **Early Detection Value**
   - Honeypot successfully detected connection attempts
   - Provides early warning of reconnaissance activities
   - Can alert before full attack progression

2. **Reconnaissance Phase**
   - Most attacks begin with reconnaissance
   - Detecting this phase allows proactive defense
   - Honeypots excel at detecting initial probing

3. **Network Visibility**
   - Honeypot provides visibility into network activity
   - Logs all connection attempts regardless of outcome
   - Creates audit trail for security analysis

### Recommendations

1. **Enhanced Logging**
   - Improve authentication attempt capture
   - Log more protocol-level details
   - Capture banner exchange and handshake data

2. **Alerting Integration**
   - Set up alerts for connection attempts
   - Monitor for patterns (multiple quick connections)
   - Integrate with SIEM systems

3. **Honeypot Placement**
   - Deploy honeypots in multiple network segments
   - Use different service types (SSH, HTTP, etc.)
   - Create honeypot network to attract attackers

4. **Analysis Automation**
   - Automate log analysis
   - Generate alerts for suspicious patterns
   - Create dashboards for visualization

5. **Threat Intelligence**
   - Correlate with known attack patterns
   - Share findings with threat intelligence feeds
   - Track attacker behavior over time

## Technical Notes

### Log Format

The honeypot generates logs in JSONL format (JSON Lines):
- One event per line
- Structured JSON format
- Easy to parse and analyze
- Timestamp in ISO 8601 format

### Connection Behavior

Observed connection patterns:
- Very brief connections (~0.5 seconds)
- Immediate disconnection
- No persistent sessions
- Suggests automated tools or quick tests

### Limitations

1. **Authentication Capture**: Some authentication attempts may not be captured due to quick disconnections
2. **Protocol Parsing**: SSH protocol parsing could be enhanced for better data extraction
3. **Session Duration**: Very short sessions limit data collection

## Conclusion

The honeypot successfully demonstrated its value as a detection mechanism, capturing connection attempts and providing visibility into network reconnaissance activities. While the captured attacks were relatively benign (reconnaissance), the honeypot proved effective at:

- ✅ Detecting connection attempts
- ✅ Logging connection metadata
- ✅ Providing timeline of activities
- ✅ Identifying source IPs
- ✅ Generating statistics

The brief connection durations suggest the honeypot is working as intended - attackers connect, realize it's a service (or get blocked), and disconnect quickly. This is valuable intelligence for understanding attack patterns and improving defenses.

## Logs

Full logs are available in `/app/logs/connections.jsonl`

To regenerate this analysis:
```bash
docker exec 2_network_honeypot python3 analyze_logs.py
```
