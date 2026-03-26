# d3kOS PWA — AtMyBoat Mobile Companion

Progressive Web App. Runs on GitHub Pages. No App Store.

## Files

| File | Purpose |
|------|---------|
| `index.html` | App shell — HTML skeleton, bottom nav |
| `app.css` | Dark marine theme, AODA AA contrast |
| `app.js` | SPA logic — login, dashboard, alerts, boatlog, settings |
| `manifest.json` | PWA manifest — enables Add to Home Screen |
| `sw.js` | Service worker — cache-first static, network-first API |
| `icons/icon.svg` | Source icon (convert to PNG before deploying) |
| `icons/ICONS_NEEDED.md` | How to generate icon-192.png + icon-512.png |

## Deploy to GitHub Pages

1. Create a new **private** GitHub repo: `SkipperDon/d3kos-pwa`
2. Copy all files from this directory to the repo root
3. Generate PNG icons (see `icons/ICONS_NEEDED.md`) and place in `icons/`
4. In repo Settings → Pages → Source: Deploy from branch → `main` / `/ (root)`
5. App URL: `https://skipperdon.github.io/d3kos-pwa/`

**Before deploying:** update `API_BASE` in `app.js` from staging URL to production:
```js
// Change this:
const API_BASE = 'https://atmyboat.com/staging/wp-content/themes/twentytwenty-child/mobile';
// To this:
const API_BASE = 'https://atmyboat.com/wp-content/themes/twentytwenty-child/mobile';
```

## Screens

- **Login** — enter WP username + password → returns app_token
- **Dashboard** — engine, position, system health, alerts summary
- **Alerts** — active unresolved alerts
- **Boatlog** — latest log entry (full history at atmyboat.com/dashboard)
- **Settings** — account info, vessel details, OTA upgrade trigger, sign out

## API Endpoints Used

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `user-login.php` | POST | none | Exchange credentials for app_token |
| `list-vessels.php` | GET | Bearer app_token | Get all paired Pis |
| `dashboard-data.php` | GET | Bearer app_token | Last known boat state |
| `command-queue.php` | POST | Bearer app_token | Send command to Pi (OTA, fix) |

## Add to Home Screen (end user)

**iOS (Safari):** Share button → "Add to Home Screen"
**Android (Chrome):** Three-dot menu → "Add to Home Screen"
**Desktop Chrome/Edge:** Install icon in address bar

Once installed, runs fullscreen with no browser chrome — feels like a native app.
