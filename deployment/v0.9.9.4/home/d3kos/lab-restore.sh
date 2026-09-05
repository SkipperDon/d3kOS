#!/bin/bash
# lab-restore.sh — BUG-104 (S148 2026-09-05)
#
# Run this AT THE PI'S LOCAL CONSOLE (keyboard + monitor) after sanitize.sh has run
# and the Pi has rebooted, if SSH will not connect.
#
# Why this is needed: sanitize.sh deletes SSH host keys as part of preparing a
# distribution image. On a genuine first boot, the OS regenerates them
# automatically (sshd-keygen.service / regenerate_ssh_host_keys.service, both
# ConditionFirstBoot=yes). The LAB Pi is never on a genuine first boot when this
# happens — that condition was already satisfied long ago — so those services are
# skipped and SSH stays dead until this script runs.
#
# NOT part of the distributed image's normal behaviour. Lives at /home/d3kos/ so it
# survives sanitize.sh (which only deletes specific named files, never this one) and
# is available locally without needing network access — the whole point, since SSH
# being down is exactly the problem this script fixes.
set -e

echo "Regenerating SSH host keys..."
sudo ssh-keygen -A

echo "Starting and enabling ssh..."
sudo systemctl enable --now ssh

echo "Done."
systemctl is-active ssh

echo ""
echo "If your authorized_keys was also wiped (sanitize.sh removes it), you still need"
echo "to add your public key manually before SSH login will accept it:"
echo "  mkdir -p ~/.ssh && chmod 700 ~/.ssh"
echo "  echo '<your public key line>' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
