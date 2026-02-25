#!/bin/bash
# Deploy Voice Watchdog System to d3kOS Pi

set -e

PI_USER="d3kos"
PI_HOST="192.168.1.237"
SSH_KEY="$HOME/.ssh/d3kos_key"

echo "=== d3kOS Voice Watchdog Deployment ==="
echo ""

# Check connection
echo "Testing SSH connection..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$PI_USER@$PI_HOST" "echo 'Connected'" &>/dev/null; then
    echo "ERROR: Cannot connect to Pi at $PI_HOST"
    echo "Please ensure Pi is powered on and connected to network"
    exit 1
fi
echo "✓ Connected to Pi"
echo ""

# Copy files to Pi
echo "Copying watchdog files to Pi..."
scp -i "$SSH_KEY" voice-watchdog.sh "$PI_USER@$PI_HOST:/tmp/"
scp -i "$SSH_KEY" d3kos-voice-watchdog.service "$PI_USER@$PI_HOST:/tmp/"
scp -i "$SSH_KEY" d3kos-voice-watchdog.timer "$PI_USER@$PI_HOST:/tmp/"
echo "✓ Files copied"
echo ""

# Install on Pi
echo "Installing watchdog on Pi..."
ssh -i "$SSH_KEY" "$PI_USER@$PI_HOST" << 'ENDSSH'
set -e

echo "Creating watchdog directory..."
sudo mkdir -p /opt/d3kos/scripts

echo "Installing watchdog script..."
sudo mv /tmp/voice-watchdog.sh /opt/d3kos/scripts/
sudo chmod +x /opt/d3kos/scripts/voice-watchdog.sh
sudo chown root:root /opt/d3kos/scripts/voice-watchdog.sh

echo "Installing systemd service..."
sudo mv /tmp/d3kos-voice-watchdog.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/d3kos-voice-watchdog.service

echo "Installing systemd timer..."
sudo mv /tmp/d3kos-voice-watchdog.timer /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/d3kos-voice-watchdog.timer

echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Enabling watchdog timer..."
sudo systemctl enable d3kos-voice-watchdog.timer

echo "Starting watchdog timer..."
sudo systemctl start d3kos-voice-watchdog.timer

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Watchdog Status:"
sudo systemctl status d3kos-voice-watchdog.timer --no-pager | head -15
echo ""
echo "Next run:"
sudo systemctl list-timers d3kos-voice-watchdog.timer --no-pager
echo ""

ENDSSH

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Watchdog will check voice service every 2 minutes"
echo ""
echo "Manual commands:"
echo "  Check status:  ssh -i $SSH_KEY $PI_USER@$PI_HOST 'systemctl status d3kos-voice-watchdog.timer'"
echo "  View logs:     ssh -i $SSH_KEY $PI_USER@$PI_HOST 'cat /var/log/d3kos-voice-watchdog.log'"
echo "  Run now:       ssh -i $SSH_KEY $PI_USER@$PI_HOST 'sudo systemctl start d3kos-voice-watchdog.service'"
echo "  Disable:       ssh -i $SSH_KEY $PI_USER@$PI_HOST 'sudo systemctl stop d3kos-voice-watchdog.timer'"
echo ""
