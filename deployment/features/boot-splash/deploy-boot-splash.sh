#!/usr/bin/env bash
# d3kOS — Deploy branded boot splash (Plymouth theme)
# Usage: ./deploy-boot-splash.sh [PI_IP]
# Requires: SSH key at ~/.ssh/id_d3kos

set -euo pipefail

PI="${1:-192.168.1.237}"
SSH_USER="d3kos"
SSH_KEY="${HOME}/.ssh/id_d3kos"
SSH="ssh -i ${SSH_KEY} -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${SSH_USER}@${PI}"
SCP="scp -i ${SSH_KEY} -o ConnectTimeout=10 -o StrictHostKeyChecking=no"
THEME_DIR="$(cd "$(dirname "$0")/theme" && pwd)"

green() { printf '\033[0;32m[OK]   %s\033[0m\n' "$1"; }
blue()  { printf '\033[0;34m[>>]   %s\033[0m\n' "$1"; }
red()   { printf '\033[0;31m[FAIL] %s\033[0m\n' "$1"; exit 1; }

echo ""
echo "d3kOS Boot Splash — Deploy Plymouth Theme"
echo "Target: ${SSH_USER}@${PI}"
echo "=================================================="

# ── Preflight ────────────────────────────────────────────────────────────────
blue "Checking Pi connectivity..."
ping -c 1 -W 3 "$PI" &>/dev/null || red "Cannot reach $PI"
$SSH "echo ok" &>/dev/null 2>&1  || red "SSH failed — check ~/.ssh/id_d3kos"
green "Pi reachable"

# ── Check Plymouth is installed ──────────────────────────────────────────────
blue "Checking Plymouth..."
$SSH "which plymouthd" &>/dev/null || {
    blue "Plymouth not found — installing..."
    $SSH "sudo apt-get install -y plymouth plymouth-themes" || red "Plymouth install failed"
}
green "Plymouth present"

# ── Create theme directory on Pi ─────────────────────────────────────────────
blue "Creating theme directory..."
$SSH "sudo mkdir -p /usr/share/plymouth/themes/d3kos"
green "Directory ready"

# ── Copy theme files ─────────────────────────────────────────────────────────
blue "Copying theme files..."
for f in d3kos.plymouth d3kos.script amboat-logo.png; do
    $SCP "${THEME_DIR}/${f}" "${SSH_USER}@${PI}:/tmp/${f}"
    $SSH "sudo mv /tmp/${f} /usr/share/plymouth/themes/d3kos/${f}"
    $SSH "sudo chmod 644 /usr/share/plymouth/themes/d3kos/${f}"
done
green "Theme files deployed"

# ── Register as default Plymouth theme ───────────────────────────────────────
blue "Registering theme as default..."
$SSH "sudo update-alternatives --install \
    /usr/share/plymouth/themes/default.plymouth \
    default.plymouth \
    /usr/share/plymouth/themes/d3kos/d3kos.plymouth \
    100" || true

$SSH "sudo update-alternatives --set \
    default.plymouth \
    /usr/share/plymouth/themes/d3kos/d3kos.plymouth" || true
green "Theme registered"

# ── Rebuild initramfs so splash appears on next boot ─────────────────────────
blue "Rebuilding initramfs (this takes ~30 seconds)..."
$SSH "sudo update-initramfs -u"
green "initramfs updated"

# ── Enable Plymouth in boot config ───────────────────────────────────────────
blue "Checking boot config for splash parameter..."
CMDLINE=$($SSH "cat /boot/firmware/cmdline.txt 2>/dev/null || cat /boot/cmdline.txt 2>/dev/null")
if echo "$CMDLINE" | grep -q "splash"; then
    green "splash already in cmdline.txt"
else
    blue "Adding 'quiet splash' to cmdline.txt..."
    $SSH "sudo sed -i 's/\$/ quiet splash plymouth.ignore-serial-consoles/' \
        /boot/firmware/cmdline.txt 2>/dev/null || \
        sudo sed -i 's/\$/ quiet splash plymouth.ignore-serial-consoles/' \
        /boot/cmdline.txt"
    green "Boot config updated"
fi

echo ""
echo "=================================================="
echo "Boot splash deployed. Reboot Pi to see it:"
echo "  ssh -i ~/.ssh/id_d3kos d3kos@${PI} 'sudo reboot'"
echo ""
echo "To update the version string in the splash:"
echo "  Edit: deployment/features/boot-splash/theme/d3kos.script"
echo "  Change: Image.Text(\"d3kOS v0.9.4\", ...)"
echo "  Re-run this script"
echo "=================================================="
