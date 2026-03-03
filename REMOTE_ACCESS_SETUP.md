# d3kOS Remote Access Setup

Remote access lets you check your boat's live data from any phone or tablet
— on the marina Wi-Fi, over cellular, or from home.

---

## What's Available

| Endpoint | Auth | Description |
|----------|------|-------------|
| `GET /remote/health` | None | Service health check |
| `GET /remote/status` | API key | All current boat metrics (engine, nav, tanks) |
| `GET /remote/maintenance` | API key | Last 20 maintenance log entries |
| `POST /remote/note` | API key | Add a maintenance note from your phone |

---

## Your API Key

The API key was set during installation:

```
t9dt7M80dgp-OHDhahXOz8kk4z41eo7YGTOv6xEn1L4
```

Include it in every request as the `X-API-Key` header.

To generate a new key at any time:
```bash
ssh d3kos@192.168.1.237
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Then update /opt/d3kos/config/api-keys.json → "remote_api_key"
```

---

## Option A — Local Network (Already Working)

On the boat's Wi-Fi you can access the Pi directly:

```bash
# From any device on the same network:
curl -H "X-API-Key: t9dt7M80dgp-OHDhahXOz8kk4z41eo7YGTOv6xEn1L4" \
     http://192.168.1.237/remote/status
```

---

## Option B — Tailscale (Recommended for True Remote Access)

Tailscale creates a private VPN between your phone and the Pi.
No port forwarding required. Works on cellular, marina Wi-Fi, home broadband.

### Step 1 — Install Tailscale on the Pi

```bash
ssh d3kos@192.168.1.237
curl -fsSL https://tailscale.com/install.sh | sudo sh
sudo tailscale up
# Copy the auth URL that appears and open it in your browser
# Log in with your Tailscale account (free tier is fine)
```

### Step 2 — Get the Pi's Tailscale IP

```bash
sudo tailscale ip -4   # e.g. 100.64.0.1
```

### Step 3 — Install Tailscale on your phone

- iOS: App Store → "Tailscale"
- Android: Play Store → "Tailscale"
- Log in with the same Tailscale account

### Step 4 — Access from anywhere

```
http://100.64.x.x/remote/status
```
(Replace with your actual Tailscale IP)

---

## Option C — Router Port Forwarding

Forward external port 8443 → Pi port 80. This exposes the Pi to the internet.
Use HTTPS (set up Let's Encrypt) if doing this — API key alone is not
sufficient security over unencrypted HTTP on the public internet.

---

## Phone Quick Test

```bash
# Health check (no key needed):
curl http://192.168.1.237/remote/health

# Full status (key required):
curl -H "X-API-Key: t9dt7M80dgp-OHDhahXOz8kk4z41eo7YGTOv6xEn1L4" \
     http://192.168.1.237/remote/status

# Add a maintenance note from your phone:
curl -X POST \
     -H "X-API-Key: t9dt7M80dgp-OHDhahXOz8kk4z41eo7YGTOv6xEn1L4" \
     -H "Content-Type: application/json" \
     -d '{"content": "Checked bilge pump — all clear"}' \
     http://192.168.1.237/remote/note
```

---

## Status Response Format

```json
{
  "timestamp": "2026-03-03T18:00:00",
  "engine": {
    "rpm": 3200,
    "oil_pressure_psi": 45.0,
    "coolant_temp_f": 180.0,
    "hours": 1547.5
  },
  "navigation": {
    "speed_kts": 12.5,
    "heading_deg": 270,
    "latitude": 44.4167,
    "longitude": -79.3333
  },
  "systems": {
    "fuel_pct": 75.0,
    "battery_v": 14.2
  }
}
```

Null values mean the sensor is unavailable or the engine is off.

---

## Service Management

```bash
sudo systemctl status d3kos-remote-api.service
sudo systemctl restart d3kos-remote-api.service
sudo journalctl -u d3kos-remote-api.service -f
```
