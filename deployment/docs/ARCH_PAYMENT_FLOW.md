# AD4 — Architecture: Payment Flows
**Version:** v1.0.0
**Date:** 2026-04-02
**Project:** AtMyBoat.com / d3kOS

---

## Summary

This document describes the three payment flows in the AtMyBoat.com platform: T2/T3 subscription upgrades via Stripe Checkout, Fix My Pi (FMP) one-time charges initiated from the PWA, and the T0→T1 pairing flow that upgrades tier without a charge. All Stripe interactions are handled on the server side (HostPapa PHP). The PWA never holds Stripe keys. The Pi never calls Stripe directly. Don clicks "Push to Live" — Claude never pushes.

---

## Flow 1 — Subscription Upgrade (T2 / T3)

User upgrades from the AtMyBoat.com website. Stripe handles the checkout session.

```
  USER BROWSER              HOSTPAPA (WordPress)         STRIPE
  ============              ====================         ======

  1. User clicks
     "Upgrade to T2/T3"
     on atmyboat.com
        |
        | POST wp-admin/admin-ajax.php
        | action=atmyboat_create_checkout
        +──────────────────────────────>
                                        | creates Stripe
                                        | Checkout Session
                                        | price_id: T2 or T3
                                        | success_url, cancel_url
                                        +───────────────────────>
                                        |
                                        <── session.url ─────────
                                        |
        <── redirect URL ───────────────+

  2. User completes
     payment on
     Stripe Checkout
        |
        | (Stripe hosted page)
        +──────────────────────────────────────────> [Stripe]
                                                          |
                                                          | payment.succeeded
                                                          | or
                                                          | checkout.session.completed
                                                          |
  3. Stripe fires webhook
                                        POST admin-ajax.php
                                        action=atmyboat_stripe_webhook
                                        <───────────────────────────────
                                        |
                                        | routes to:
                                        | inc/stripe-webhook.php
                                        |
                                        | validates webhook secret
                                        | reads customer → WP user
                                        |
                                        | UPDATE wp_usermeta:
                                        | atmyboat_tier = 'T2' or 'T3'
                                        |
                                        | POST 200 → Stripe ──────────>

  4. Pi tier sync
     (next 30min export)

  RASPBERRY PI                HOSTPAPA
  ============                ========

  [export_worker.py]
        |
        | POST data-ingress.php
        +──────────────────────────────>
                                        |
                                        | reads atmyboat_tier
                                        | from wp_usermeta
                                        |
        <── response: { tier: "T2" } ──+
        |
        | updates license.json:
        | tier = T2
        | tier_service re-reads file
```

---

## Flow 2 — Fix My Pi (FMP) Charge

Initiated from the PWA. Stripe charges the user's saved card. Pi executes the fix. Auto-refund if Pi does not respond in time.

```
  PWA (app.js)          HOSTPAPA PHP             STRIPE          RASPBERRY PI
  ============          ============             ======          ============

  1. User taps
     "Fix My Pi"
     in PWA
        |
        | POST fix-my-pi-app.php
        | Header: app_token
        | body: { issue_type }
        +─────────────────────>
                               |
                               | validates app_token
                               | looks up Stripe
                               | customer for user
                               |
                               | creates Stripe charge:
                               | amount: $29.99
                               | price_id: FMP
                               +──────────────────>
                               |
                               <── charge.id ──────
                               |
        <── { charge_id,
              command_id } ───+

  2. Stripe webhook fires
     on charge success
                               POST admin-ajax.php
                               action=atmyboat_stripe_webhook
                               <────────────────────────────── [Stripe]
                               |
                               | routes to:
                               | fix-my-pi-billing.php
                               |
                               | validates webhook secret
                               |
                               | INSERT amboat_command_queue:
                               | command = 'fix_my_pi'
                               | issue_type = [from charge metadata]
                               | status = 'pending'
                               | timeout_at = NOW + 10min
                               |

  3. Pi picks up command
                               [command-queue.php]
                               <─────────────────────────────── [cloud_agent.py]
                               | (polls every 30s)               Pi
                               |
                               | returns: fix_my_pi command
                               +──────────────────────────────>
                               |
                               | Pi runs fix_my_pi.py
                               | executes diagnostics,
                               | applies fixes
                               |
  4. Pi ACKs result
                               POST app-command.php
                               action=ack
                               body: { command_id, result }
                               <───────────────────────────────
                               |
                               | UPDATE amboat_command_queue:
                               | status = 'complete'
                               | result = payload
                               |

  5. PWA polls for result
        |
        | GET app-command.php
        | ?command_id=xxx
        +─────────────────────>
                               |
                               | returns: { status, result }
                               |
        <── result displayed ──+

  6. Auto-refund (timeout path — Pi did not respond)

     [fix-my-pi-billing.php checks timeout_at]
        |
        | if NOW > timeout_at AND status = 'pending'
        |
        | Stripe refund: charge_id
        +──────────────────────────────────────────> [Stripe API]
        |
        | UPDATE command: status = 'timeout_refunded'
        |
        | (PWA poll returns: { status: 'refunded' })
```

---

## Flow 3 — T0 → T1 Pairing (No Charge)

When a registered user pairs their Pi, the device is automatically upgraded to T1. No payment involved.

```
  PWA (app.js)          HOSTPAPA PHP             RASPBERRY PI
  ============          ============             ============

  1. User logs in to
     atmyboat.com
     WordPress session
     established

  2. PWA requests pairing
        |
        | POST pair-device.php
        | Header: app_token
        | body: { device_token }
        +─────────────────────>
                               |
                               | validates app_token
                               | validates device_token
                               | links: WP user ↔ device
                               |
                               | reads current tier for user
                               | if tier = T0:
                               |   SET atmyboat_tier = T1
                               |
                               | returns: { tier: "T1", ... }
                               |
        <── { tier: "T1" } ────+
        |
        | PWA updates UI
        | to reflect T1

  3. Pi reads updated tier
     on next export cycle

  [export_worker.py]
        |
        | POST data-ingress.php
        +─────────────────────>
                               |
                               | response: { tier: "T1" }
                               |
        <── response ──────────+
        |
        | license.json updated
        | tier_service re-reads
```

---

## Stripe Price IDs

| Product | Price ID (alias) | Amount | Interval |
|---|---|---|---|
| Fix My Pi | FMP price_id | $29.99 | One-time |
| T2 Subscription | T2 price_id | $9.99 | Monthly |
| T3 Subscription | T3 price_id | $99.99 | Annual |

Actual price IDs are stored in `inc/atmyboat-config.php` via `define()`. Never hardcode in PHP templates or JS.

---

## Webhook Secret Validation

Both subscription and FMP webhooks validate the Stripe signature before processing:

```php
$sig = $_SERVER['HTTP_STRIPE_SIGNATURE'];
$event = \Stripe\Webhook::constructEvent($payload, $sig, STRIPE_WEBHOOK_SECRET);
```

Two separate webhook secrets are configured:
- `STRIPE_WEBHOOK_SECRET` — subscription events
- `STRIPE_WEBHOOK_SECRET_FMP` — Fix My Pi charge events

Both secrets are defined in `inc/atmyboat-config.php`. See AD5 (ARCH_CREDENTIAL_MAP.md) for storage details.

---

## Notes

- All Stripe calls are server-side PHP only. The PWA never holds a Stripe key. The Pi never calls Stripe.
- The FMP timeout window (default 10 minutes) is set in fix-my-pi-billing.php. If the Pi is offline, the auto-refund fires after timeout_at is exceeded on the next billing check sweep.
- T1 is granted automatically on Pi pairing (no Stripe event). T2 and T3 require a Stripe subscription event. T0 is the default unregistered state.
- Tier changes propagate to the Pi on the next export_worker cycle (up to 30 minutes). For FMP, the command is queued immediately after the Stripe webhook fires and picked up by cloud_agent within 30 seconds.
- Never run WPReset on the live site. Never push to live directly — Don clicks "Push to Live" in cPanel.
- The AI model cap for website AI is claude-haiku-4-5-20251001 at a hard $30/month limit in Anthropic Console.
