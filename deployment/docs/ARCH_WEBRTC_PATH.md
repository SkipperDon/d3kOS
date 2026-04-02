# AD3 — Architecture: WebRTC Live Tunnel Path
**Version:** v1.0.0
**Date:** 2026-04-02
**Project:** AtMyBoat.com / d3kOS

---

## Summary

This document describes the WebRTC peer-to-peer live tunnel between the PWA and the Raspberry Pi. The connection uses STUN for NAT traversal in most network environments and falls back to a Metered.ca TURN relay when symmetric NAT or CGNAT blocks direct P2P. Signaling is handled by a polling-based PHP endpoint on HostPapa. The Pi never accepts inbound connections — it always initiates outbound. TURN build-out is deferred to v1.1 pending field testing results.

---

## Connection Establishment — Sequence Diagram

```
  PWA (GitHub Pages)        HOSTPAPA PHP              RASPBERRY PI
  ==================        ============              ============

  1. User opens Live View
     in app.js
        |
        | GET turn-credentials.php
        | Header: app_token
        +─────────────────────>
                               |
                               | calls Metered.ca API
                               | returns ICE server list:
                               |   STUN: stun.l.google.com:19302
                               |   STUN: stun.cloudflare.com:3478
                               |   TURN: a.relay.metered.ca (creds)
                               |
        <─────────────────────+
        | { iceServers: [...] }
        |
  2. PWA creates
     RTCPeerConnection
     with ICE server list
        |
        | POST rtc-signal.php
        | action=offer
        | payload: SDP offer
        | Header: app_token
        +─────────────────────>
                               |
                               | writes offer to DB:
                               | signaling record
                               | status = 'pending'
                               |
  3. Pi polls for signal
                               |          GET rtc-signal.php
                               |          action=poll
                               |          Header: AMBOAT_API_KEY
                               |          + device_token
                               <──────────────────────────────
                               |
                               | returns: SDP offer
                               |
                               +──────────────────────────────>
                               |
  4. Pi processes offer,
     gathers ICE candidates
        |
        |          POST rtc-signal.php
        |          action=answer
        |          payload: SDP answer
        |          + ICE candidates
        <──────────────────────────────────────────────────────
                               |
                               | stores answer
                               |
  5. PWA polls for answer
        |
        | GET rtc-signal.php
        | action=poll
        | Header: app_token
        +─────────────────────>
                               |
                               | returns: SDP answer
                               | + ICE candidates
                               |
        <─────────────────────+
        |
  6. ICE Negotiation begins
```

---

## ICE Candidate Resolution

ICE tries candidates in priority order. The first working path is used.

```
  PWA                      NETWORK PATH                   Pi
  ===                      ============                   ==

  Candidate 1:             Direct LAN
  Local IP  ─────────────────────────────────────────>  Local IP
  (host)    <─────────────────────────────────────────  (host)
             SUCCESS if both on same LAN segment

  Candidate 2:             STUN / Internet
  STUN reflexive ─────────────────────────────────────> STUN reflexive
  (srflx)        <───────────────────────────────────── (srflx)
                  stun.l.google.com:19302
                  stun.cloudflare.com:3478
                  SUCCESS if neither side is behind
                  symmetric NAT or CGNAT

  Candidate 3:             TURN Relay (fallback)
  TURN relay ──────────> a.relay.metered.ca <────────── TURN relay
  (relay)    <────────────────────────────── ─────────> (relay)
                  USED when STUN fails (CGNAT,
                  symmetric NAT on either side)
```

---

## Active Data Channel (Post-Connection)

Once the peer connection is established and the data channel opens:

```
  PWA ◄──────────────────────────────────────────────── Pi
        Real-time sensor data (JSON, streaming)
        Camera snapshots (binary / base64)
        Alert events (JSON)

  PWA ──────────────────────────────────────────────── Pi
        Control commands (JSON)
        Config requests
        Camera control signals
```

Data channel is bidirectional. Pi sends data continuously; PWA sends control messages on demand.

---

## Key Design Constraints

| Constraint | Rule |
|---|---|
| Pi inbound ports | NONE open. Pi always initiates outbound only. |
| Signaling channel | Polling-based (rtc-signal.php) — no persistent WebSocket to HostPapa |
| TURN usage | Fallback only. Credentials are per-session, not stored persistently. |
| TURN build-out | Deferred to v1.1. v0.9.4 ships with STUN + credential fetch only. |
| Symmetry | Pi uses same rtc-signal.php endpoint as PWA but with AMBOAT_API_KEY auth |

---

## Component Responsibilities

| Component | Location | Responsibility |
|---|---|---|
| turn-credentials.php | HostPapa | Calls Metered.ca API, returns ICE server list with per-session TURN creds |
| rtc-signal.php | HostPapa | Polling-based SDP offer/answer and ICE candidate exchange |
| live_session.py | Pi :8090 | WebRTC peer, handles ICE, opens data channel, streams sensor data |
| app.js (WebRTC section) | PWA | Creates RTCPeerConnection, fetches TURN creds, exchanges SDP via polling |
| STUN servers | External | Google stun.l.google.com:19302, Cloudflare stun.cloudflare.com:3478 |
| TURN server | Metered.ca | a.relay.metered.ca — relay fallback for CGNAT environments |

---

## Version Roadmap

| Version | WebRTC Scope |
|---|---|
| v0.9.4 | STUN + TURN credential fetch + polling signaling. TURN available but not tested in field. |
| v1.0 | Field testing determines if TURN is actually needed. If STUN succeeds in all test boats: TURN remains as cold fallback. |
| v1.1 | Option C (self-hosted UDP hole-punching coordination server) replaces STUN/Metered.ca dependency if cost or reliability warrants it. NOT built in v0.9.4. |

---

## Notes

- Tailscale was evaluated and rejected as the Pi connectivity solution. It must be removed from the Pi before v0.9.4 build begins. Do not repurpose or re-enable Tailscale for any reason.
- The polling interval for rtc-signal.php on the Pi side is set in live_session.py. If signaling latency is high (>2s), check the polling interval before assuming a network issue.
- Metered.ca TURN credentials are short-lived (TTL set by Metered.ca). The PWA must fetch fresh credentials each time it initiates a connection — do not cache or reuse old credentials across sessions.
- If STUN resolution fails on both Google and Cloudflare servers simultaneously, the connection will fall through to TURN automatically via the ICE candidate priority mechanism. No code change required to activate TURN fallback.
- The STUN servers (Google, Cloudflare) are free and require no API key or account.
