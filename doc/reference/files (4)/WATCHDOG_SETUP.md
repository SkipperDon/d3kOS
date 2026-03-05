# TrueNAS VM Watchdog — Full Setup & Troubleshooting Guide

## Your Problem Summary

| Issue | Cause | Fix |
|---|---|---|
| Bridge drops after power event | NIC/bridge state not restored on resume | Watchdog + bridge reset |
| SSH unreachable from other AI agents | Bridge or guest IP lost | Auto-restart + static IP |
| virtio network not working | Driver mismatch or bridge misconfiguration | See Section 2 |
| No auto-recovery | No watchdog present | vm-watchdog.sh (Section 1) |

---

## Section 1 — Install the Watchdog

### Step 1: Copy the script to TrueNAS host

```bash
# SSH into TrueNAS host (not the VM)
scp vm-watchdog.sh root@truenas-ip:/root/vm-watchdog.sh
ssh root@truenas-ip
chmod +x /root/vm-watchdog.sh
```

### Step 2: Edit the CONFIG block

Open `/root/vm-watchdog.sh` and set:
```bash
VM_NAME="ubuntu-ollama"      # Must match exactly what shows in TrueNAS UI
VM_IP="192.168.1.100"        # Your Ubuntu VM's static IP
PLATFORM="SCALE"             # or "CORE" if on TrueNAS CORE 13
NOTIFY_EMAIL="you@email.com" # TrueNAS must have email configured under Alerts
NTFY_TOPIC="truenas-alerts"  # Optional: install ntfy app on phone for push alerts
```

### Step 3: Add to TrueNAS Cron

**Via TrueNAS UI:**
> System → Advanced → Cron Jobs → Add

| Field | Value |
|---|---|
| Description | VM Watchdog |
| Command | `/root/vm-watchdog.sh` |
| Run As User | `root` |
| Schedule | `*/2 * * * *` (every 2 minutes) |
| Hide Standard Output | ✓ |

**Or via CLI:**
```bash
# Add to crontab directly
echo "*/2 * * * * /root/vm-watchdog.sh" | crontab -
```

### Step 4: Test it
```bash
# Dry run
/root/vm-watchdog.sh

# Watch live log
tail -f /var/log/vm-watchdog.log

# Simulate failure (temporarily wrong IP to test alert)
```

---

## Section 2 — Fix virtio Network (Most Likely Culprit)

### Diagnosis First

**On TrueNAS SCALE host:**
```bash
# Check if bridge exists and has VM tap attached
ip link show
bridge link show

# Find your VM's vnet/tap interface
virsh domiflist ubuntu-ollama

# TrueNAS names bridges as bridge0, bridge1 etc — NOT br0
# Check for errors on the bridge
ip -s link show bridge0
journalctl -n 100 | grep -i "virtio\|bridge[0-9]\|tap\|vnet"
```

**On TrueNAS CORE host:**
```bash
ifconfig -a | grep -E "tap|epair|bridge"
dmesg | grep -i virtio
```

### Fix A: Wrong NIC model in VM config

If virtio_net isn't loading in the guest, try switching the NIC emulation:
> TrueNAS UI → Virtualization → Your VM → Edit → Network → Device Type

Change from `VirtIO` → `e1000` temporarily to confirm network works, then switch back.

### Fix B: Bridge interface down after power event

The host bridge may not auto-recover after unclean shutdown:
```bash
# SCALE — restart the bridge
# TrueNAS names bridges as bridge0, bridge1, etc. — NOT br0
BRIDGE_NAME="bridge0"   # Check yours with: virsh domiflist <vmname>
ip link set $BRIDGE_NAME down
sleep 2
ip link set $BRIDGE_NAME up

# Or restart the whole networking stack
systemctl restart networking   # Debian-based SCALE
```

### Fix C: Guest virtio_net driver not loading

Inside the Ubuntu VM (use console, not SSH, since network is down):
```bash
# Check if virtio_net module is loaded
lsmod | grep virtio

# Load it manually
sudo modprobe virtio_net

# Make it persistent
echo "virtio_net" | sudo tee -a /etc/modules

# Check the interface came up
ip a
# If interface exists but no IP:
sudo dhclient -v ens3   # replace ens3 with your interface name
```

### Fix D: Network Manager not managing the interface

```bash
# Inside Ubuntu VM
sudo nmcli device status
sudo nmcli device connect ens3   # use your interface name

# Or edit netplan (Ubuntu 20.04+)
sudo nano /etc/netplan/00-installer-config.yaml
```

Example netplan config with STATIC IP (recommended — avoids DHCP dependency):
```yaml
network:
  version: 2
  ethernets:
    ens3:
      dhcp4: no
      addresses: [192.168.1.100/24]
      gateway4: 192.168.1.1
      nameservers:
        addresses: [8.8.8.8, 1.1.1.1]
```
```bash
sudo netplan apply
```

### Fix E: Use Serial Console as fallback access

**Always configure serial console so you can access the VM even when network is dead.**

In Ubuntu VM, enable serial console:
```bash
sudo systemctl enable serial-getty@ttyS0.service
sudo systemctl start serial-getty@ttyS0.service
```

In TrueNAS SCALE, connect via:
```bash
virsh console ubuntu-ollama
# Press Ctrl+] to exit
```

---

## Section 3 — Auto-Recovery Inside the Ubuntu VM

Install a watchdog daemon inside the guest to handle kernel hangs and I/O freezes:

```bash
# Inside Ubuntu VM
sudo apt install watchdog -y
sudo nano /etc/watchdog.conf
```

Add/uncomment these lines:
```
max-load-1     = 24
max-load-5     = 18
watchdog-device = /dev/watchdog
watchdog-timeout = 60
interval        = 10
ping            = 192.168.1.1    # Your TrueNAS host IP
file            = /var/log/syslog
change          = 1407
```

```bash
sudo systemctl enable watchdog
sudo systemctl start watchdog
```

> ⚠️ The hardware watchdog `/dev/watchdog` requires the `iTCO_wdt` or `softdog` module:
```bash
sudo modprobe softdog
echo "softdog" | sudo tee -a /etc/modules
```

---

## Section 4 — Prevent Bridge Loss After Power Events

### On TrueNAS SCALE

Create a systemd service that re-validates the bridge on startup:
```bash
cat > /etc/systemd/system/vm-bridge-check.service << 'EOF'
[Unit]
Description=Validate VM bridge on boot
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/root/vm-watchdog.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl enable vm-bridge-check.service
```

### On TrueNAS CORE

Add to `/etc/rc.local` or use TrueNAS Init/Shutdown Scripts:
> System → Advanced → Init/Shutdown Scripts → Add
- Type: `Command`
- Command: `/root/vm-watchdog.sh`
- When: `Post Init`

---

## Section 5 — Notification via ntfy (Recommended for Phone Alerts)

1. Install the **ntfy** app on your phone (iOS/Android)
2. Subscribe to topic: `truenas-alerts` (or any name you set)
3. In watchdog config set: `NTFY_TOPIC="truenas-alerts"`

Test it:
```bash
curl -d "Test from watchdog" https://ntfy.sh/truenas-alerts
```

---

## Section 6 — Watchdog Log Patterns Reference

| Log Pattern | Meaning | Action |
|---|---|---|
| `VM is reachable ✓` | All good | None |
| `VM unreachable (failure #1)` | First miss, waiting | Automatic |
| `Bridge reset` | Network glitch fixed | Monitor |
| `Full restart` | Serious issue | Check VM logs |
| `Restart loop detected` | Persistent failure | Manual intervention |
| `OOM events detected` | RAM exhaustion | Increase VM RAM |
| `bridge/virtio errors` | Network layer issue | Check bridge config |

---

## Quick Reference Commands

```bash
# TrueNAS SCALE
virsh list --all               # List all VMs
virsh start ubuntu-ollama      # Start VM
virsh reboot ubuntu-ollama     # Graceful reboot
virsh reset ubuntu-ollama      # Hard reset (like pressing power button)
virsh console ubuntu-ollama    # Serial console access
virsh domiflist ubuntu-ollama  # List VM network interfaces

# TrueNAS CORE
midclt call virt.instance.query  # List VMs
midclt call virt.instance.start '{"id":"ubuntu-ollama"}'
midclt call virt.instance.stop  '{"id":"ubuntu-ollama","force":true}'

# Watch watchdog live
tail -f /var/log/vm-watchdog.log
```
