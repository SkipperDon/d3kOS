# Entity: TrueNAS + Verify Agent

*Last updated: S86 2026-05-21 | Sources: project_truenas_smb_s63.md, MEMORY.md, DEPLOYMENT_INDEX.md*

---

## Identity

- **IP:** 192.168.1.102
- **OS:** TrueNAS 13.0-U6.2 — **FreeBSD-based, NOT Linux**
- **NetBIOS name:** TEYKO2SERVER
- **SSH:** port 22
- **Status:** SMB fully operational (fixed S63)

---

## Verify Agent

An independent code reviewer hosted on TrueNAS. Reviews Claude Code output against the project codebase before changes are accepted. Documented at `deployment/docs/VERIFY_AGENT.md`.

---

## Critical: FreeBSD Differences

TrueNAS runs FreeBSD. Linux assumptions break here:

| Linux | FreeBSD (TrueNAS) |
|-------|-------------------|
| `systemctl` | `service` (e.g. `service smbd status`) |
| `/etc/samba/smb.conf` | `/usr/local/etc/smb4.conf` |
| `/var/log/syslog` | `/var/log/messages` |
| `netstat -tuln` | Different flags |

---

## SMB Shares

| Share | Type |
|-------|------|
| Beaver | Disk share |
| Cheeta | Disk share |
| Mice | Disk share |

**User:** `user1` (UID 1002). Windows access: `\\192.168.1.102` → username `user1`.

---

## SMB Failure: Disk Full (S63 root cause)

SMB fails on boot with `messaging_dgm_init: bind failed: No space left on device` when `/var/db/system/` fills up.

**Cleanup (S63):**
```bash
find /var/db/system/syslog-* -type f -mtime +7 -delete
find /var/db/system/rrd-* -type f -mtime +30 -delete
find /var/db/system -type f -mtime +30 -delete
```

**Watch:** `/var/db/system/update/` — 847M not cleaned S63. Monitor this folder.

**Disk check:**
```bash
df -h | grep -E 'Small3gigs|Capacity'
```

---

## Related

- [[entities/d3kos-platform]] — Verify Agent reviews d3kOS code changes
- [[entities/admin-console-vm]] — other infrastructure node on the LAN
