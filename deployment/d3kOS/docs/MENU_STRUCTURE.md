# d3kOS Menu Structure
**Date:** 2026-03-13
**Version:** 1.0

## Before (Original Pi Menu)
- Navigation → OpenCPN (Flatpak, no .desktop in /usr/share/applications — not in system menu)
- No d3kOS menu category

## After (d3kOS v2.0)

### d3kOS Menu Category
All entries use Category `X-d3kOS;Network;` and validate via `desktop-file-validate`.

| Entry | Exec | File |
|-------|------|------|
| d3kOS Dashboard | `chromium --app=http://localhost:3000 --start-fullscreen` | d3kos-dashboard.desktop |
| OpenCPN (Fallback) | `flatpak run org.opencpn.OpenCPN` | d3kos-opencpn.desktop |
| AvNav Charts | `chromium --app=http://localhost:8080 --start-maximized` | d3kos-avnav.desktop |
| Gemini Marine Assistant | `chromium --app=http://localhost:3001 --start-maximized` | d3kos-gemini-nav.desktop |

### Files on Pi
```
/home/d3kos/.local/share/applications/d3kos-dashboard.desktop
/home/d3kos/.local/share/applications/d3kos-opencpn.desktop
/home/d3kos/.local/share/applications/d3kos-avnav.desktop
/home/d3kos/.local/share/applications/d3kos-gemini-nav.desktop
/home/d3kos/.local/share/desktop-directories/d3kOS.directory
/home/d3kos/.config/menus/applications-merged/d3kOS.menu
```

### Backup
```
/home/d3kos/backups/d3kos-menu-backup-2026-03-13/
  lxde-applications.menu
  gnome-applications.menu
  rpd-applications.menu
  BACKUP_LOG.txt
```

## Infrastructure (hidden from all menus)
- OpenPlotter: http://localhost:8081 — GPS, AIS, NMEA
- Signal K: http://localhost:8099 — data broker
- d3kOS Dashboard API: http://localhost:3000 — Flask (Phase 2)
- Issue Detector: http://localhost:8199 — self-healing (moved from 8099 for SK migration)

## Port Migration (2026-03-13)
Signal K was on :3000 (default). Moved to :8099 to free :3000 for the Flask dashboard.
issue_detector.py was on :8099. Moved to :8199.

## Rollback Instructions

### Rollback port migration
```bash
# Revert issue_detector port (on Pi as d3kos user)
sudo sed -i 's/port=8199/port=8099/' /opt/d3kos/services/self-healing/issue_detector.py
sudo systemctl restart d3kos-issue-detector

# Revert Signal K port
sudo sed -i '/Environment=PORT=8099/d' /etc/systemd/system/signalk.service
sudo systemctl daemon-reload && sudo systemctl restart signalk

# Revert nginx
sudo sed -i 's|http://127.0.0.1:8199|http://localhost:8099|g' /etc/nginx/sites-enabled/default
sudo sed -i 's|http://127.0.0.1:8099/signalk/|http://localhost:3000/signalk/|g' /etc/nginx/sites-enabled/default
sudo systemctl reload nginx
```

### Rollback menu files
```bash
rm -f /home/d3kos/.local/share/applications/d3kos-*.desktop
rm -f /home/d3kos/.local/share/desktop-directories/d3kOS.directory
rm -f /home/d3kos/.config/menus/applications-merged/d3kOS.menu
```
