# Entity: Admin Console VM

*Last updated: S86 2026-05-21 | Sources: MEMORY.md, reference_admin_console_vm.md*

---

## Identity

- **IP:** 192.168.236.5 (VirtualBox Host-Only network)
- **User:** skipper
- **OS:** Ubuntu 22.04.5 LTS
- **Role:** CRM admin interface for d3kOS fleet/subscription management

---

## Services

| File | Purpose |
|------|---------|
| `/home/d3kos-admin/app.py` | Flask CRM app (deployed from repo `app_patched.py`) |
| `/home/d3kos-admin/templates/` | Jinja2 templates |
| `admin-crm.service` | systemd service name |

**Flask startup state:** NOT started as systemd — currently launched with `nohup`. Dies on reboot. Systemd service setup is a deferred open item.

---

## Access Pattern (Windows only)

WSL **cannot** reach 192.168.236.5 — Host-Only network times out from WSL.

All VM access is via Windows:
- SSH: `plink.exe` 
- File copy: `pscp.exe`

---

## Deploy Pattern (confirmed S24/S55)

```
pscp.exe upload → /tmp/
plink.exe: sudo cp /tmp/<file> <destination>
plink.exe: sudo systemctl restart admin-crm.service
```

For sudo without a TTY: `echo 'PASS' | sudo -S bash -c '...'`

**NEVER** `cat file | plink "echo pass | sudo -S tee"` — sudo consumes stdin before tee, file is zeroed. Confirmed dangerous — do not use.

**Repo → VM name mapping:** `app_patched.py` in repo deploys as `app.py` on VM.

---

## HostPapa CRM Proxy (permanent architecture)

Remote MySQL on HostPapa is permanently blocked. The VM reaches HostPapa data via PHP proxy.

```
Flask (VM 192.168.236.5)
    │
    └── HTTPS POST (ADMIN_API_KEY) ──→ crm-proxy.php (HostPapa)
                                             │
                                             └── mysqli (127.0.0.1) ──→ MySQL
```

See [[concepts/php-proxy-pattern]] for full detail.

**`admin-api.php` NO LONGER EXISTS** — renamed to `crm-proxy.php` in S58 (ImunifyAV-flagged). `admin-config.php` holds credentials separately (never committed).

---

## MySQL Rule

Always `127.0.0.1` — never `localhost` on HostPapa. `localhost` uses socket (breaks periodically on shared hosting); `127.0.0.1` uses TCP.

---

## CRM Auth Keys

| Key | Used By |
|-----|---------|
| `ADMIN_API_KEY` | CRM-facing PHP files (crm-proxy.php, issue-api.php, admin-api-tickets.php) — hardcoded inline, NOT from config.php |
| `AMBOAT_API_KEY` | Pi-facing endpoints only |

---

## HostPapa FTP Paths

- FTP root = `home/` (not `public_html/`)
- **Staging:** `staging/wp-content/themes/twentytwenty-child/` from FTP root
- **Live:** `wp-content/themes/twentytwenty-child/` (no staging prefix — live since Phase 4 S55e)
- FTP deploy via Python ftplib only — bash breaks `!` in passwords
- FTP: port 21 FTPS, host `ftp.atmyboat.com`, user `d3kos@atmyboat.com`

---

## Open Item

- Flask is not running as systemd — dies on reboot. P3 live SSH Pi health check from VM (192.168.236.5 → Pi 192.168.1.237) also not confirmed.

---

## Related

- [[entities/atmyboat-website]] — HostPapa hosting that CRM manages
- [[concepts/php-proxy-pattern]] — the VM→HostPapa data access pattern
- [[entities/tier-system]] — tier updates flow through CRM → crm-proxy.php
