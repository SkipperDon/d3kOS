# d3kOS Gemini AI Setup

## Get a Free API Key
1. Visit https://aistudio.google.com
2. Sign in with Google account
3. Click "Get API key" → Create API key
4. Copy the key (starts with AIza...)

## Configure in d3kOS
1. Open Settings → AI Assistant — Gemini API section
2. Paste API key → Save Configuration
3. Click Test Connection (should show "Connected!")

## Models
- **gemini-1.5-flash**: Fast, free tier, recommended for voice use
- **gemini-2.0-flash**: Latest, very fast
- **gemini-1.5-pro**: Most capable, may use paid quota

## How It Works
- **Rule-based queries** (RPM, oil, temp, fuel, etc.) → answered instantly (0.17s), no AI call
- **Complex queries** → Gemini responds in 2-4s (vs 6-8s OpenRouter)
- **No API key** → falls back to manual RAG search results
- API key is stored on Pi at `/opt/d3kos/config/api-keys.json` (chmod 600, never exposed to browser)

## Voice Integration
After configuration, saying "Helm, [question]" uses Gemini automatically for complex queries.
Rule-based engine data responses still answer instantly.

## Service Details
- Service: `d3kos-gemini-proxy.service`
- Port: 8097 (internal), proxied via nginx at `/gemini/`
- Endpoints: `/gemini/health`, `/gemini/chat`, `/gemini/test`, `/gemini/config`
