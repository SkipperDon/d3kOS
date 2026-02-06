# HELM-OS NETWORK SPECIFICATION

**Version**: 2.0
**Date**: February 6, 2026
**Based on**: MASTER_SYSTEM_SPEC.md v2.0

---

## TABLE OF CONTENTS

1. [Network Overview](#network-overview)
2. [WiFi Access Point](#wifi-access-point)
3. [Ethernet Configuration](#ethernet-configuration)
4. [Network Services](#network-services)
5. [Firewall Configuration](#firewall-configuration)
6. [Service Discovery](#service-discovery)
7. [NMEA2000 Integration](#nmea2000-integration)
8. [Security](#security)
9. [Performance & Bandwidth](#performance--bandwidth)
10. [Troubleshooting](#troubleshooting)

---

## 1. NETWORK OVERVIEW

### 1.1 Network Architecture

Helm-OS creates a dual-interface network configuration:

```
┌────────────────────────────────────────────────┐
│             Raspberry Pi 4                     │
│                                                │
│  ┌──────────┐              ┌──────────┐       │
│  │  wlan0   │              │  eth0    │       │
│  │ (WiFi AP)│              │(Ethernet)│       │
│  │10.42.0.1 │              │  DHCP    │       │
│  └────┬─────┘              └────┬─────┘       │
│       │                         │             │
│  ┌────┴─────────────────────────┴──────┐      │
│  │      Network Services                │     │
│  │  HTTP:80, Signal K:3000, NR:1880    │     │
│  └─────────────────────────────────────┘      │
│                                                │
└────────────────────────────────────────────────┘
         │                         │
         │ WiFi                    │ Ethernet
         │                         │
    ┌────▼─────┐              ┌────▼──────┐
    │ Mobile   │              │ Boat      │
    │ Devices  │              │ Network   │
    │ Tablets  │              │ (Switch)  │
    │ Laptops  │              │           │
    └──────────┘              └────┬──────┘
                                   │
                              ┌────▼──────┐
                              │ IP Camera │
                              │  Router   │
                              │  Internet │
                              └───────────┘
```

### 1.2 Network Interfaces

| Interface | Type | IP Assignment | Purpose |
|-----------|------|---------------|---------|
| **wlan0** | WiFi AP | Static (10.42.0.1/24) | User access, dashboard, configuration |
| **eth0** | Ethernet | DHCP client | Boat network, internet, camera |
| **can0** | CAN Bus | N/A | NMEA2000 marine data |
| **lo** | Loopback | 127.0.0.1 | Local services |

### 1.3 Design Principles

- **Offline-First**: All core functionality works without internet
- **WiFi Access Point**: Always available for user access
- **Isolated Networks**: WiFi clients isolated from ethernet (security)
- **Internet Sharing**: Optional sharing from ethernet to WiFi
- **Local Services Only**: No external dependencies

---

## 2. WIFI ACCESS POINT

### 2.1 Configuration

**Default Settings**:
```ini
SSID: Helm-OS
Password: helm-os-2026
Security: WPA2-PSK
Channel: Auto (2.4GHz or 5GHz based on Pi 4 capability)
IP Address: 10.42.0.1/24
DHCP Range: 10.42.0.2 - 10.42.0.254
DNS Server: 10.42.0.1 (Pi itself)
Gateway: 10.42.0.1
```

### 2.2 NetworkManager Configuration

**Connection File**: `/etc/NetworkManager/system-connections/Helm-OS-AP`

```ini
[connection]
id=Helm-OS-AP
type=wifi
autoconnect=true
interface-name=wlan0

[wifi]
mode=ap
ssid=Helm-OS
band=bg
channel=6

[wifi-security]
key-mgmt=wpa-psk
psk=helm-os-2026

[ipv4]
method=shared
address=10.42.0.1/24
dns=8.8.8.8;8.8.4.4;
```

### 2.3 hostapd Configuration (Alternative)

If using hostapd instead of NetworkManager:

**File**: `/etc/hostapd/hostapd.conf`

```ini
interface=wlan0
driver=nl80211
ssid=Helm-OS
hw_mode=g
channel=6
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=helm-os-2026
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

### 2.4 DHCP Server (dnsmasq)

**File**: `/etc/dnsmasq.conf`

```ini
interface=wlan0
dhcp-range=10.42.0.2,10.42.0.254,255.255.255.0,24h
dhcp-option=3,10.42.0.1     # Gateway
dhcp-option=6,10.42.0.1     # DNS server
server=8.8.8.8              # Upstream DNS
server=8.8.4.4

# Local domain
domain=helm-os.local
local=/helm-os.local/

# DHCP reservations (optional)
dhcp-host=00:11:22:33:44:55,tablet,10.42.0.10
dhcp-host=aa:bb:cc:dd:ee:ff,phone,10.42.0.11
```

### 2.5 Access Point Performance

| Metric | Specification |
|--------|---------------|
| **WiFi Standard** | 802.11ac (WiFi 5) |
| **Frequency** | 2.4 GHz / 5 GHz (Pi 4 supports both) |
| **Theoretical Speed** | Up to 300 Mbps (2.4GHz), 867 Mbps (5GHz) |
| **Practical Throughput** | 50-100 Mbps (sufficient for dashboard) |
| **Max Clients** | 32 (practical limit: 10 for best performance) |
| **Range** | ~30 meters indoors, ~100 meters outdoors (line of sight) |

### 2.6 Recommended Channel Selection

**2.4 GHz**:
- Channels 1, 6, 11 (non-overlapping)
- Use WiFi analyzer to find least congested channel
- Marine environments typically have less interference

**5 GHz**:
- More channels available (36, 40, 44, 48, etc.)
- Better throughput but shorter range
- Less interference from other devices

---

## 3. ETHERNET CONFIGURATION

### 3.1 Ethernet Modes

#### Mode 1: DHCP Client (Default)

Raspberry Pi gets IP from boat network router/switch:

```bash
# /etc/network/interfaces.d/eth0
auto eth0
iface eth0 inet dhcp
```

**Use Cases**:
- Integration with existing boat network
- Access to IP cameras on same network
- Internet connectivity for updates
- Connection to existing NMEA2000 gateway

#### Mode 2: Static IP

Manual IP configuration for specific boat network:

```bash
# /etc/network/interfaces.d/eth0
auto eth0
iface eth0 inet static
    address 192.168.1.100
    netmask 255.255.255.0
    gateway 192.168.1.1
    dns-nameservers 8.8.8.8 8.8.4.4
```

**Use Cases**:
- Fixed IP required by boat network policy
- Easier troubleshooting (IP doesn't change)
- Integration with other marine equipment

### 3.2 Internet Sharing

**Enable Internet Sharing** (WiFi clients use Pi as gateway):

```bash
# Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# Make persistent
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

# NAT rules (iptables)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT

# Save rules
iptables-save > /etc/iptables/rules.v4
```

**Auto-Detection Script** (`/opt/helm-os/scripts/network-check.sh`):

```bash
#!/bin/bash
# Check if ethernet has internet, enable sharing if yes

if ping -c 1 -W 2 8.8.8.8 &> /dev/null; then
    echo "Internet detected on eth0, enabling sharing"
    nmcli connection modify Helm-OS-AP ipv4.method shared
    systemctl restart NetworkManager
else
    echo "No internet on eth0, standalone mode"
fi
```

### 3.3 Ethernet Performance

| Metric | Specification |
|--------|---------------|
| **Speed** | Gigabit (1000 Mbps) |
| **Auto-negotiation** | Yes (10/100/1000) |
| **Duplex** | Full duplex |
| **Cable Type** | Cat5e minimum, Cat6 recommended |
| **Max Cable Length** | 100 meters (328 feet) |
| **PoE Support** | No (use USB-C for power) |

---

## 4. NETWORK SERVICES

### 4.1 Service Ports

| Service | Protocol | Port | Interface | Purpose |
|---------|----------|------|-----------|---------|
| **HTTP (Main Menu)** | TCP | 80 | wlan0, lo | Web interface |
| **Signal K Server** | WebSocket/HTTP | 3000 | wlan0, lo | Marine data hub |
| **Node-RED** | HTTP | 1880 | wlan0, lo | Dashboard & flows |
| **RTSP (Camera)** | TCP | 554 | eth0, lo | Camera stream (Tier 2+) |
| **SSH** | TCP | 22 | wlan0 only | Remote administration (disabled by default) |
| **mDNS** | UDP | 5353 | wlan0, eth0 | Service discovery |
| **DHCP Server** | UDP | 67 | wlan0 | IP assignment |
| **DNS Server** | UDP | 53 | wlan0 | Name resolution |

### 4.2 Service Access URLs

**From WiFi Clients**:
- Main Menu: `http://helm-os.local` or `http://10.42.0.1`
- Dashboard: `http://helm-os.local:1880/dashboard`
- Signal K: `http://helm-os.local:3000`
- Signal K Admin: `http://helm-os.local:3000/@signalk/server-admin-ui`
- Camera (Tier 2+): `rtsp://helm-os.local:554/camera`

**From Localhost** (SSH/console):
- Main Menu: `http://localhost`
- Dashboard: `http://localhost:1880/dashboard`
- Signal K: `http://localhost:3000`

### 4.3 Service Binding

Services bind to specific interfaces for security:

```javascript
// Node-RED - listen on all interfaces
settings.js:
uiHost: "0.0.0.0",
uiPort: 1880,

// Signal K - listen on all interfaces
settings.json:
{
  "interfaces": {
    "admin": "0.0.0.0",
    "appstore": "0.0.0.0"
  },
  "port": 3000
}
```

### 4.4 Service Dependencies

```
Network Services Startup Order:

1. NetworkManager (network interfaces)
2. dnsmasq (DHCP/DNS)
3. avahi-daemon (mDNS)
4. signalk.service (marine data)
5. nodered.service (dashboard)
6. helm-*.service (custom services)
```

---

## 5. FIREWALL CONFIGURATION

### 5.1 UFW (Uncomplicated Firewall)

**Enable UFW**:
```bash
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

### 5.2 Firewall Rules

```bash
# Allow services on WiFi interface (wlan0)
sudo ufw allow in on wlan0 to any port 80 proto tcp comment 'HTTP'
sudo ufw allow in on wlan0 to any port 3000 proto tcp comment 'Signal K'
sudo ufw allow in on wlan0 to any port 1880 proto tcp comment 'Node-RED'
sudo ufw allow in on wlan0 to any port 554 proto tcp comment 'RTSP Camera'
sudo ufw allow in on wlan0 to any port 22 proto tcp comment 'SSH (optional)'

# Allow mDNS
sudo ufw allow in on wlan0 to any port 5353 proto udp comment 'mDNS'

# Block SSH on ethernet (security)
sudo ufw deny in on eth0 to any port 22 proto tcp comment 'Block SSH on ethernet'

# Allow DHCP
sudo ufw allow in on wlan0 to any port 67 proto udp comment 'DHCP server'
sudo ufw allow in on wlan0 to any port 53 proto udp comment 'DNS server'

# Allow established connections
sudo ufw allow in on wlan0 from 10.42.0.0/24 comment 'WiFi subnet'

# Allow CAN bus (local only)
# No firewall rules needed (not IP-based)
```

### 5.3 Rate Limiting

Prevent brute-force attacks:

```bash
# Rate limit SSH
sudo ufw limit ssh comment 'Rate limit SSH'

# Rate limit HTTP (optional, may affect dashboard)
# sudo ufw limit 80/tcp comment 'Rate limit HTTP'
```

### 5.4 View Firewall Status

```bash
# Show rules
sudo ufw status numbered

# Show verbose
sudo ufw status verbose

# Show listening ports
sudo netstat -tulpn
```

### 5.5 Firewall Configuration File

**UFW Rules**: `/etc/ufw/user.rules`

```
# Generated by Helm-OS setup
*filter
:ufw-user-input - [0:0]
:ufw-user-output - [0:0]
:ufw-user-forward - [0:0]

### RULES ###
# Allow HTTP on wlan0
-A ufw-user-input -i wlan0 -p tcp --dport 80 -j ACCEPT

# Allow Signal K on wlan0
-A ufw-user-input -i wlan0 -p tcp --dport 3000 -j ACCEPT

# Allow Node-RED on wlan0
-A ufw-user-input -i wlan0 -p tcp --dport 1880 -j ACCEPT

# Allow RTSP on wlan0 (camera)
-A ufw-user-input -i wlan0 -p tcp --dport 554 -j ACCEPT

# Block SSH on eth0
-A ufw-user-input -i eth0 -p tcp --dport 22 -j DROP

### END RULES ###
COMMIT
```

---

## 6. SERVICE DISCOVERY

### 6.1 mDNS (Avahi)

**Hostname Resolution**:
- `helm-os.local` resolves to 10.42.0.1 on WiFi network
- Uses Avahi daemon for Bonjour/Zeroconf

**Configuration**: `/etc/avahi/avahi-daemon.conf`

```ini
[server]
host-name=helm-os
domain-name=local
use-ipv4=yes
use-ipv6=no
allow-interfaces=wlan0,eth0
deny-interfaces=lo

[publish]
publish-addresses=yes
publish-hinfo=yes
publish-workstation=no
publish-domain=yes
```

### 6.2 Advertised Services

**Service Files**: `/etc/avahi/services/`

**HTTP Service** (`/etc/avahi/services/http.service`):
```xml
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">Helm-OS Web Interface</name>
  <service>
    <type>_http._tcp</type>
    <port>80</port>
    <txt-record>path=/</txt-record>
  </service>
</service-group>
```

**Signal K Service** (`/etc/avahi/services/signalk.service`):
```xml
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">Helm-OS Signal K</name>
  <service>
    <type>_signalk-http._tcp</type>
    <port>3000</port>
    <txt-record>path=/signalk</txt-record>
  </service>
</service-group>
```

**Node-RED Service** (`/etc/avahi/services/nodered.service`):
```xml
<?xml version="1.0" standalone='no'?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
  <name replace-wildcards="yes">Helm-OS Node-RED</name>
  <service>
    <type>_node-red._tcp</type>
    <port>1880</port>
  </service>
</service-group>
```

### 6.3 Service Discovery Testing

```bash
# List all mDNS services
avahi-browse -a -t

# Check specific service
avahi-browse -r _http._tcp

# Resolve hostname
avahi-resolve -n helm-os.local

# Check if hostname is published
avahi-resolve-host-name helm-os.local
```

---

## 7. NMEA2000 INTEGRATION

### 7.1 CAN Bus Network

**Physical Layer**:
- Protocol: ISO 11898 (CAN 2.0B)
- Bitrate: 250 kbps (NMEA2000 standard)
- Bus Topology: Linear with 120Ω termination at each end
- Max Cable Length: 200m backbone, 6m drop cables
- Voltage: 12V DC nominal (9-16V operating range)

**CAN Interface**: `can0` (SocketCAN)

### 7.2 CAN0 Configuration

**Network Interface Configuration** (`/etc/network/interfaces.d/can0`):

```bash
auto can0
iface can0 inet manual
    pre-up /sbin/ip link set can0 type can bitrate 250000
    up /sbin/ifconfig can0 up
    down /sbin/ifconfig can0 down
```

**Systemd Service** (`/etc/systemd/system/can0.service`):

```ini
[Unit]
Description=CAN0 Interface
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/ip link set can0 type can bitrate 250000
ExecStart=/sbin/ifconfig can0 up
ExecStop=/sbin/ifconfig can0 down

[Install]
WantedBy=multi-user.target
```

### 7.3 NMEA2000 Data Flow

```
NMEA2000 Bus (CAN)
      ↓
  PiCAN-M HAT (MCP2515)
      ↓
  SocketCAN (can0)
      ↓
Signal K Server (actisense plugin)
      ↓
WebSocket (port 3000)
      ↓
Node-RED Dashboard
      ↓
User Interface
```

### 7.4 CAN Bus Monitoring

```bash
# View CAN interface status
ip -details link show can0

# Monitor CAN traffic
candump can0

# Filter specific PGN (e.g., 127488 = Engine RPM)
candump can0 | grep 127488

# Send test frame
cansend can0 1FFFFFFF#0011223344556677

# View CAN statistics
ip -s -d link show can0
```

### 7.5 NMEA2000 Network Diagnostics

**Check Bus Voltage**:
```bash
# Measure voltage between NMEA2000 power (12V) and ground
# Should read: 11-14.5V (boat electrical system)
```

**Check Termination**:
```bash
# Measure resistance between CAN-H (white) and CAN-L (blue)
# Should read: ~60Ω (two 120Ω resistors in parallel)
```

**Check for Bus Errors**:
```bash
# Monitor for errors
dmesg | grep can0

# Check error counters
ip -s link show can0 | grep errors
```

---

## 8. SECURITY

### 8.1 Network Security Layers

```
┌─────────────────────────────────────────┐
│         Application Security            │
│  - Service authentication (optional)    │
│  - Session management                   │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Network Security                │
│  - UFW firewall rules                   │
│  - Interface isolation                  │
│  - Rate limiting                        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         WiFi Security                   │
│  - WPA2-PSK encryption                  │
│  - Strong password                      │
│  - Hidden SSID (optional)               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Physical Security               │
│  - Enclosure access control             │
│  - SD card read-only (optional)         │
└─────────────────────────────────────────┘
```

### 8.2 WiFi Security Best Practices

**Default Password** (change during onboarding):
- Default: `helm-os-2026`
- Minimum: 12 characters
- Recommended: 16+ characters, mixed case, numbers, symbols
- Avoid: Dictionary words, boat name, owner name

**Change WiFi Password**:
```bash
# Using nmcli
sudo nmcli connection modify Helm-OS-AP wifi-sec.psk "new_password_here"
sudo nmcli connection up Helm-OS-AP

# Manually edit
sudo nano /etc/NetworkManager/system-connections/Helm-OS-AP
# Change 'psk=' line
sudo systemctl restart NetworkManager
```

**Optional: Hidden SSID**:
```bash
# Hide SSID (security through obscurity)
sudo nmcli connection modify Helm-OS-AP wifi.hidden yes
sudo nmcli connection up Helm-OS-AP
```

### 8.3 SSH Security

**Disable SSH by Default**:
```bash
sudo systemctl stop ssh
sudo systemctl disable ssh
```

**Enable SSH Temporarily** (for troubleshooting):
```bash
# Enable for current session only
sudo systemctl start ssh

# Enable permanently
sudo systemctl enable ssh
sudo systemctl start ssh
```

**SSH Configuration** (`/etc/ssh/sshd_config`):
```ini
# Strong security settings
Port 22
PermitRootLogin no
PasswordAuthentication yes
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
ChallengeResponseAuthentication no
UsePAM yes
X11Forwarding no
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server

# Only allow from WiFi interface
ListenAddress 10.42.0.1

# Rate limiting (fail2ban)
MaxAuthTries 3
MaxSessions 2
```

### 8.4 Service Authentication (Optional)

**Node-RED Password Protection**:

Edit `/home/pi/.node-red/settings.js`:

```javascript
adminAuth: {
    type: "credentials",
    users: [{
        username: "admin",
        password: "$2b$08$...", // bcrypt hash
        permissions: "*"
    }]
}
```

Generate password hash:
```bash
node-red admin hash-pw
```

**Signal K Authentication**:

Configure in Signal K Admin UI:
- Navigate to: `http://helm-os.local:3000/@signalk/server-admin-ui`
- Security → Users → Add User
- Set username and password

### 8.5 Network Isolation

**WiFi Client Isolation** (prevent clients from seeing each other):

```bash
# Using hostapd
# Add to /etc/hostapd/hostapd.conf:
ap_isolate=1
```

**VLAN Segregation** (advanced):
- Separate VLAN for camera (IP camera traffic isolated)
- Separate VLAN for management (SSH, web admin)
- Not typically needed for Helm-OS

---

## 9. PERFORMANCE & BANDWIDTH

### 9.1 Bandwidth Requirements

| Service | Typical Usage | Peak Usage | Notes |
|---------|---------------|------------|-------|
| **Signal K Updates** | 5-10 KB/s | 20 KB/s | Real-time marine data |
| **Dashboard Refresh** | 1-2 KB/s | 5 KB/s | Gauge updates at 1Hz |
| **Camera Stream** (Tier 2+) | 5 MB/s | 10 MB/s | 1080p @ 30fps H.264 |
| **Voice Audio** (Tier 2+) | 50 KB/s | 100 KB/s | 16kHz 16-bit mono |
| **Web UI** | 100-500 KB | 2 MB | Initial page load |
| **OpenCPN Charts** | Negligible | 10 MB | Chart downloads (one-time) |

**Total Bandwidth**:
- Core features: < 50 KB/s
- With voice: < 150 KB/s
- With camera: < 10 MB/s

**WiFi Capacity**: 50-100 Mbps (Pi 4 WiFi), plenty of headroom

### 9.2 Latency Requirements

| Service | Target Latency | Acceptable Max |
|---------|----------------|----------------|
| **Dashboard Updates** | < 100ms | 500ms |
| **Signal K WebSocket** | < 50ms | 200ms |
| **Camera Stream** | < 500ms | 1000ms |
| **Voice Response** | < 2000ms | 3000ms |
| **Web Page Load** | < 1000ms | 3000ms |

### 9.3 Network Performance Monitoring

**Bandwidth Monitoring**:
```bash
# Install iftop
sudo apt install iftop

# Monitor wlan0 traffic
sudo iftop -i wlan0

# Monitor eth0 traffic
sudo iftop -i eth0

# View cumulative stats
ifstat -i wlan0 1
```

**Latency Testing**:
```bash
# Ping from client to Pi
ping helm-os.local

# Expected: < 10ms on WiFi

# Test Signal K WebSocket latency
# Use browser developer tools (Network tab)
```

**Throughput Testing**:
```bash
# Install iperf3
sudo apt install iperf3

# Server mode (on Pi)
iperf3 -s

# Client mode (from laptop/tablet)
iperf3 -c helm-os.local

# Expected: 50-100 Mbps on WiFi
```

### 9.4 Performance Optimization

**WiFi Performance Tips**:
1. Use 5GHz WiFi when possible (less interference)
2. Position Pi centrally in boat (better coverage)
3. Limit simultaneous camera streams to 1-2
4. Use hardware-accelerated video decode (GPU)
5. Disable unused services

**Network Stack Tuning** (`/etc/sysctl.conf`):
```ini
# Increase buffer sizes for better throughput
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216

# Reduce latency
net.ipv4.tcp_low_latency=1
net.ipv4.tcp_no_metrics_save=1
```

---

## 10. TROUBLESHOOTING

### 10.1 WiFi Access Point Issues

**Problem**: WiFi AP not visible

**Diagnostic Steps**:
```bash
# Check wlan0 status
ip link show wlan0

# Check NetworkManager status
sudo systemctl status NetworkManager

# Check for conflicts (no wpa_supplicant should be running)
ps aux | grep wpa_supplicant

# Restart AP
sudo nmcli connection down Helm-OS-AP
sudo nmcli connection up Helm-OS-AP

# View logs
journalctl -u NetworkManager -f
```

**Problem**: Can't connect to WiFi (wrong password)

**Solutions**:
1. Verify password: `sudo nmcli connection show Helm-OS-AP | grep psk`
2. Reset to default: `sudo nmcli connection modify Helm-OS-AP wifi-sec.psk helm-os-2026`
3. Restart AP: `sudo nmcli connection up Helm-OS-AP`

**Problem**: WiFi connected but no internet

**Diagnostic**:
```bash
# Check if Pi has internet
ping -c 3 8.8.8.8

# Check IP forwarding enabled
cat /proc/sys/net/ipv4/ip_forward
# Should output: 1

# Check NAT rules
sudo iptables -t nat -L -v

# Test DNS resolution
nslookup google.com
```

### 10.2 Service Access Issues

**Problem**: Can't access dashboard at helm-os.local

**Solutions**:
1. Try IP address instead: `http://10.42.0.1:1880/dashboard`
2. Check mDNS: `avahi-resolve -n helm-os.local`
3. Restart Avahi: `sudo systemctl restart avahi-daemon`
4. Check firewall: `sudo ufw status`
5. Verify service running: `sudo systemctl status nodered`

**Problem**: Signal K not responding

**Diagnostic**:
```bash
# Check service
sudo systemctl status signalk

# Check port listening
sudo netstat -tulpn | grep 3000

# View logs
journalctl -u signalk -f

# Test locally
curl http://localhost:3000/signalk/v1/api/
```

**Problem**: Camera stream not loading (Tier 2+)

**Diagnostic**:
```bash
# Ping camera
ping 192.168.1.100

# Test RTSP stream
ffprobe rtsp://admin:password@192.168.1.100:554/h264Preview_01_main

# Check firewall
sudo ufw status | grep 554

# Test VLC playback
vlc rtsp://admin:password@192.168.1.100:554/h264Preview_01_main
```

### 10.3 NMEA2000 Network Issues

**Problem**: No CAN0 data

**Diagnostic**:
```bash
# Check CAN interface exists
ip link show can0

# Check interface status (should be UP)
ip -details link show can0

# Monitor for traffic
candump can0
# If nothing appears, check hardware

# Check for errors
dmesg | grep -i can
dmesg | grep -i mcp251x

# Verify PiCAN-M detected
lsmod | grep mcp251x
```

**Problem**: CAN bus errors

**Diagnostic**:
```bash
# Check error counters
ip -s link show can0 | grep errors

# Check for bus-off condition
# Error counters > 255 = bus-off

# Solutions:
# 1. Check termination resistors (60Ω total)
# 2. Verify CAN-H/CAN-L not swapped
# 3. Check 12V power present on bus
# 4. Reduce bitrate (test only): ip link set can0 type can bitrate 125000
```

### 10.4 Ethernet Issues

**Problem**: No ethernet connection

**Diagnostic**:
```bash
# Check link status
ip link show eth0

# Check for DHCP lease
ip addr show eth0

# Check cable (LED lights on RJ45 port?)
ethtool eth0

# Test connectivity
ping -c 3 192.168.1.1  # Gateway
ping -c 3 8.8.8.8      # Internet

# Restart interface
sudo ip link set eth0 down
sudo ip link set eth0 up
```

**Problem**: Slow ethernet performance

**Diagnostic**:
```bash
# Check negotiated speed
ethtool eth0 | grep Speed
# Should be: 1000Mb/s

# Force gigabit (test only)
sudo ethtool -s eth0 speed 1000 duplex full autoneg off

# Check for errors
ethtool -S eth0 | grep -i error

# Test with iperf3
iperf3 -c <server_ip>
```

### 10.5 DNS Resolution Issues

**Problem**: helm-os.local not resolving

**Diagnostic**:
```bash
# Check Avahi running
sudo systemctl status avahi-daemon

# Test resolution
avahi-resolve -n helm-os.local

# Check mDNS packets
sudo tcpdump -i wlan0 port 5353

# Restart Avahi
sudo systemctl restart avahi-daemon

# Flush DNS cache (on client device)
# Windows: ipconfig /flushdns
# macOS: sudo dscacheutil -flushcache
# Linux: sudo systemd-resolve --flush-caches
```

### 10.6 Network Performance Issues

**Problem**: Slow dashboard response

**Diagnostic**:
```bash
# Check CPU usage
top

# Check network latency
ping -c 10 helm-os.local

# Check bandwidth usage
sudo iftop -i wlan0

# Check for interference (WiFi)
sudo iwlist wlan0 scan | grep -E 'Channel|Quality'

# Change WiFi channel if congested
sudo nmcli connection modify Helm-OS-AP wifi.channel 11
sudo nmcli connection up Helm-OS-AP
```

---

## APPENDIX A: Network Commands Reference

### A.1 WiFi Commands

```bash
# Show WiFi status
nmcli device wifi

# List connections
nmcli connection show

# Show AP details
nmcli connection show Helm-OS-AP

# Restart AP
nmcli connection down Helm-OS-AP && nmcli connection up Helm-OS-AP

# Change SSID
nmcli connection modify Helm-OS-AP wifi.ssid "New-SSID"

# Change password
nmcli connection modify Helm-OS-AP wifi-sec.psk "new_password"

# Change channel
nmcli connection modify Helm-OS-AP wifi.channel 11
```

### A.2 Ethernet Commands

```bash
# Show interface status
ip addr show eth0

# Show link details
ip -details link show eth0

# Restart interface
ip link set eth0 down && ip link set eth0 up

# Show routing table
ip route

# Show ARP table
ip neigh

# Check physical link
ethtool eth0
```

### A.3 Firewall Commands

```bash
# Show all rules
sudo ufw status numbered

# Add rule
sudo ufw allow from 10.42.0.0/24 to any port 80

# Delete rule
sudo ufw delete [number]

# Reset firewall
sudo ufw reset

# Enable/disable
sudo ufw enable
sudo ufw disable
```

### A.4 Service Commands

```bash
# Check service status
sudo systemctl status signalk
sudo systemctl status nodered
sudo systemctl status avahi-daemon

# Restart service
sudo systemctl restart signalk

# View logs
journalctl -u signalk -f

# Check listening ports
sudo netstat -tulpn | grep LISTEN
```

---

## APPENDIX B: Network Configuration Files

### B.1 Key Configuration Files

| File | Purpose |
|------|---------|
| `/etc/NetworkManager/system-connections/Helm-OS-AP` | WiFi AP configuration |
| `/etc/network/interfaces.d/eth0` | Ethernet configuration |
| `/etc/network/interfaces.d/can0` | CAN bus configuration |
| `/etc/dnsmasq.conf` | DHCP/DNS server |
| `/etc/avahi/avahi-daemon.conf` | mDNS configuration |
| `/etc/avahi/services/*.service` | Service advertisements |
| `/etc/ufw/user.rules` | Firewall rules |
| `/etc/hosts` | Local hostname resolution |
| `/etc/sysctl.conf` | Network stack tuning |

### B.2 Backup Network Configuration

```bash
#!/bin/bash
# Backup all network configs

BACKUP_DIR="/opt/helm-os/backups/network_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Copy configurations
cp /etc/NetworkManager/system-connections/* $BACKUP_DIR/
cp /etc/network/interfaces.d/* $BACKUP_DIR/
cp /etc/dnsmasq.conf $BACKUP_DIR/
cp /etc/avahi/avahi-daemon.conf $BACKUP_DIR/
cp -r /etc/avahi/services $BACKUP_DIR/
sudo iptables-save > $BACKUP_DIR/iptables.rules

echo "Network configuration backed up to: $BACKUP_DIR"
```

---

## APPENDIX C: Default Network Settings

### C.1 Factory Default Settings

```
WiFi Access Point:
  SSID: Helm-OS
  Password: helm-os-2026
  IP Address: 10.42.0.1/24
  DHCP Range: 10.42.0.2 - 10.42.0.254

Ethernet:
  Mode: DHCP Client
  Fallback IP: 192.168.1.100/24

Services:
  HTTP: Port 80
  Signal K: Port 3000
  Node-RED: Port 1880
  RTSP: Port 554 (Tier 2+)

Security:
  SSH: Disabled
  Firewall: Enabled (UFW)
  WiFi Encryption: WPA2-PSK
```

### C.2 Reset to Factory Defaults

```bash
#!/bin/bash
# Reset network to factory defaults

# WiFi AP
sudo nmcli connection modify Helm-OS-AP wifi.ssid "Helm-OS"
sudo nmcli connection modify Helm-OS-AP wifi-sec.psk "helm-os-2026"
sudo nmcli connection modify Helm-OS-AP ipv4.addresses "10.42.0.1/24"

# Ethernet (DHCP)
sudo nmcli connection modify eth0 ipv4.method auto

# Restart networking
sudo systemctl restart NetworkManager

# Reset firewall
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow in on wlan0 to any port 80
sudo ufw allow in on wlan0 to any port 3000
sudo ufw allow in on wlan0 to any port 1880
sudo ufw enable

echo "Network reset to factory defaults"
```

---

**END OF NETWORK SPECIFICATION**
