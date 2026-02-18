#!/bin/bash
# configure-network.sh - Configure WiFi AP and ethernet sharing
# Part of d3kOS Distribution Preparation
# Session-Dist-2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log "Starting d3kOS network configuration..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root (use sudo)"
    exit 1
fi

# Configuration variables
WIFI_SSID="d3kOS"
WIFI_PASSWORD="d3kos2026"
ETHERNET_SUBNET="10.42.0.0/24"
HOSTNAME="d3kos"

# Set hostname
log "Setting hostname to '$HOSTNAME'..."
hostnamectl set-hostname "$HOSTNAME"
echo "127.0.1.1 $HOSTNAME" >> /etc/hosts

# Configure WiFi Access Point
log "Configuring WiFi Access Point '$WIFI_SSID'..."

NMCONNECTION_FILE="/etc/NetworkManager/system-connections/d3kos.nmconnection"

cat > "$NMCONNECTION_FILE" <<EOF
[connection]
id=d3kos
uuid=$(uuidgen)
type=wifi
autoconnect=true
interface-name=wlan0

[wifi]
mode=ap
ssid=$WIFI_SSID
band=bg
channel=6

[wifi-security]
key-mgmt=wpa-psk
psk=$WIFI_PASSWORD

[ipv4]
method=shared
address1=10.42.0.1/24

[ipv6]
addr-gen-mode=default
method=disabled

[proxy]
EOF

chmod 600 "$NMCONNECTION_FILE"
log "  WiFi AP configuration created: $NMCONNECTION_FILE"

# Configure ethernet sharing
log "Configuring ethernet sharing on 10.42.0.0/24..."

ETH_NMCONNECTION="/etc/NetworkManager/system-connections/Wired-connection-1.nmconnection"

cat > "$ETH_NMCONNECTION" <<EOF
[connection]
id=Wired connection 1
uuid=$(uuidgen)
type=ethernet
autoconnect-priority=999
interface-name=eth0
timestamp=$(date +%s)

[ethernet]

[ipv4]
method=shared
address1=10.42.0.1/24

[ipv6]
addr-gen-mode=default
method=disabled

[proxy]
EOF

chmod 600 "$ETH_NMCONNECTION"
log "  Ethernet sharing configuration created: $ETH_NMCONNECTION"

# Configure dnsmasq for DHCP and DNS
log "Configuring dnsmasq..."

DNSMASQ_DIR="/etc/NetworkManager/dnsmasq-shared.d"
mkdir -p "$DNSMASQ_DIR"

# Main dnsmasq config for shared connections
cat > "$DNSMASQ_DIR/d3kos-shared.conf" <<EOF
# d3kOS dnsmasq configuration for shared connections
# Created by configure-network.sh

# DHCP range for WiFi AP and ethernet sharing
dhcp-range=10.42.0.50,10.42.0.250,24h

# DNS
domain=d3kos.local
local=/d3kos.local/

# Host record for d3kOS
address=/d3kos.local/10.42.0.1

# DHCP options
dhcp-option=option:router,10.42.0.1
dhcp-option=option:dns-server,10.42.0.1

# Logging (disable in production, enable for debugging)
# log-queries
# log-dhcp
EOF

log "  dnsmasq shared config created: $DNSMASQ_DIR/d3kos-shared.conf"

# Camera DHCP reservation (if camera exists)
log "  Checking for camera DHCP reservation..."
if [ ! -f "$DNSMASQ_DIR/camera-reservation.conf" ]; then
    log "  Creating camera DHCP reservation template..."
    cat > "$DNSMASQ_DIR/camera-reservation.conf" <<EOF
# Camera DHCP reservation
# Reolink RLC-810A - Update MAC address when camera is connected
# dhcp-host=ec:71:db:f9:7c:7c,10.42.0.100,infinite
EOF
    log "  Template created: $DNSMASQ_DIR/camera-reservation.conf"
    log "  Update MAC address when camera is connected"
else
    log "  Camera reservation already exists"
fi

# Enable IP forwarding
log "Enabling IP forwarding..."
echo "net.ipv4.ip_forward=1" > /etc/sysctl.d/99-d3kos-forwarding.conf
sysctl -p /etc/sysctl.d/99-d3kos-forwarding.conf

# Configure firewall (iptables) for NAT
log "Configuring NAT firewall rules..."

# Flush existing rules
iptables -t nat -F
iptables -F

# Enable NAT for shared connections
iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# Allow forwarding
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
iptables -A FORWARD -i eth0 -o wlan0 -j ACCEPT

# Save iptables rules
log "Saving iptables rules..."
if command -v iptables-save &>/dev/null; then
    iptables-save > /etc/iptables/rules.v4 2>/dev/null || {
        mkdir -p /etc/iptables
        iptables-save > /etc/iptables/rules.v4
    }
    log "  iptables rules saved"
fi

# Reload NetworkManager
log "Reloading NetworkManager..."
systemctl reload NetworkManager || warn "Could not reload NetworkManager"

# Summary
log ""
log "=========================================="
log "Network Configuration Complete!"
log "=========================================="
log "WiFi AP SSID: $WIFI_SSID"
log "WiFi Password: $WIFI_PASSWORD"
log "Ethernet Subnet: $ETHERNET_SUBNET"
log "Hostname: $HOSTNAME"
log "DNS: d3kos.local → 10.42.0.1"
log ""
log "Reboot or restart NetworkManager to apply:"
log "  sudo systemctl restart NetworkManager"
log "=========================================="

exit 0
