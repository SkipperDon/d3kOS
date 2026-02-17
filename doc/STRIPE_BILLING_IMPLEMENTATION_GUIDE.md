# Stripe Billing Implementation Guide for d3kOS
## Version 1.0 - February 16, 2026

---

## Table of Contents

1. [Development Time Breakdown](#development-time-breakdown)
2. [Prerequisites & Setup](#prerequisites--setup)
3. [Phase 1: Stripe Billing Setup](#phase-1-stripe-billing-setup)
4. [Phase 2: Backend API Development](#phase-2-backend-api-development)
5. [Phase 3: Mobile App Integration](#phase-3-mobile-app-integration)
6. [Phase 4: Testing & Deployment](#phase-4-testing--deployment)
7. [Ongoing Maintenance](#ongoing-maintenance)

---

## Development Time Breakdown

**Total Estimate: 40-60 hours**

### Why This Takes Time (You're Building an Entire Payment Infrastructure)

"You do all the work" means YOU (or your development team) must build:
- Backend webhook handlers
- Database schema for subscriptions
- API endpoints for mobile app
- iOS in-app purchase integration
- Android in-app purchase integration
- Subscription management UI
- Testing infrastructure

**Stripe is a tool, not a complete solution. It provides:**
- ✅ Payment processing infrastructure
- ✅ Subscription billing logic
- ✅ Customer portal (hosted)
- ✅ Webhook notifications
- ✅ API for creating/managing subscriptions

**But YOU must build:**
- ❌ Backend to receive webhooks
- ❌ Database to store subscription records
- ❌ API for mobile app to check tier status
- ❌ iOS/Android in-app purchase integration
- ❌ Logic to upgrade/downgrade tiers
- ❌ Failed payment handling
- ❌ Mobile app subscription UI

---

## Detailed Hour Breakdown

### **Phase 1: Stripe Billing Setup (4-6 hours)**

#### 1.1 Account Setup (1 hour)
- [ ] Create Stripe account (free)
- [ ] Verify business information
- [ ] Set up test mode and production mode
- [ ] Generate API keys (test + production)
- [ ] Configure webhook endpoints
- [ ] Set up Stripe CLI for local testing

**Tasks:**
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe
# OR
wget https://github.com/stripe/stripe-cli/releases/latest/download/stripe_linux_amd64.tar.gz

# Login to Stripe
stripe login

# Forward webhooks to local dev server
stripe listen --forward-to localhost:5000/api/v1/webhooks/stripe
```

#### 1.2 Product & Price Configuration (1 hour)
- [ ] Create Tier 2 Monthly product ($9.99/month)
- [ ] Create Tier 3 Annual product ($99.99/year)
- [ ] Set up recurring billing intervals
- [ ] Configure trial periods (optional)
- [ ] Set up promo codes/coupons (optional)

**Stripe Dashboard:**
```
Products → Create Product
  Name: d3kOS Tier 2 - Premium Monthly
  Description: Premium features with AI analysis and OTA updates
  Pricing: $9.99 USD / month (recurring)
  Product ID: prod_tier2_monthly
  Price ID: price_tier2_monthly_999

Products → Create Product
  Name: d3kOS Tier 3 - Enterprise Annual
  Description: Enterprise features with unlimited resets and fleet management
  Pricing: $99.99 USD / year (recurring)
  Product ID: prod_tier3_annual
  Price ID: price_tier3_annual_9999
```

#### 1.3 Webhook Configuration (1-2 hours)
- [ ] Create webhook endpoint in Stripe Dashboard
- [ ] Select events to monitor:
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_succeeded`
  - `invoice.payment_failed`
  - `customer.subscription.trial_will_end`
- [ ] Get webhook signing secret
- [ ] Test webhook delivery

**Webhook URL:**
```
https://api.d3kos.com/api/v1/webhooks/stripe
```

#### 1.4 Customer Portal Setup (1 hour)
- [ ] Enable Stripe Customer Portal
- [ ] Configure portal features:
  - ✅ Cancel subscription
  - ✅ Update payment method
  - ✅ View invoice history
  - ✅ Switch billing interval (monthly ↔ annual)
- [ ] Customize branding (d3kOS logo, colors)
- [ ] Test customer portal flow

---

### **Phase 2: Backend API Development (16-24 hours)**

This is where most time is spent. You're building the entire subscription management backend.

#### 2.1 Database Schema (2-3 hours)

**Create 3 new tables:**

**Table 1: `subscriptions`**
```sql
CREATE TABLE subscriptions (
  subscription_id VARCHAR(50) PRIMARY KEY,
  installation_id VARCHAR(16) NOT NULL,
  tier INTEGER NOT NULL CHECK (tier IN (2, 3)),
  status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'past_due', 'canceled', 'expired')),

  payment_provider VARCHAR(20) NOT NULL CHECK (payment_provider IN ('stripe', 'apple_iap', 'google_play', 'paypal')),
  provider_subscription_id VARCHAR(100) NOT NULL,
  provider_customer_id VARCHAR(100),

  started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  current_period_start TIMESTAMP NOT NULL,
  current_period_end TIMESTAMP NOT NULL,
  canceled_at TIMESTAMP NULL,
  expires_at TIMESTAMP NULL,

  amount_cents INTEGER NOT NULL,
  currency VARCHAR(3) NOT NULL DEFAULT 'USD',
  billing_interval VARCHAR(10) NOT NULL CHECK (billing_interval IN ('month', 'year')),

  trial_start TIMESTAMP NULL,
  trial_end TIMESTAMP NULL,

  last_payment_at TIMESTAMP NULL,
  next_payment_at TIMESTAMP NULL,
  payment_failed_count INTEGER DEFAULT 0,

  user_email VARCHAR(255),
  user_name VARCHAR(255),

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_installation_id (installation_id),
  INDEX idx_status (status),
  INDEX idx_provider_subscription_id (provider_subscription_id),
  FOREIGN KEY (installation_id) REFERENCES installations(installation_id)
);
```

**Table 2: `payments`**
```sql
CREATE TABLE payments (
  payment_id VARCHAR(50) PRIMARY KEY,
  installation_id VARCHAR(16) NOT NULL,
  subscription_id VARCHAR(50) NOT NULL,

  provider_payment_id VARCHAR(100) NOT NULL,
  amount_cents INTEGER NOT NULL,
  currency VARCHAR(3) NOT NULL DEFAULT 'USD',

  status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'succeeded', 'failed', 'refunded')),
  failure_reason TEXT NULL,

  invoice_url TEXT NULL,
  receipt_url TEXT NULL,

  paid_at TIMESTAMP NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_installation_id (installation_id),
  INDEX idx_subscription_id (subscription_id),
  INDEX idx_status (status),
  FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
  FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
);
```

**Table 3: `tier_upgrades`**
```sql
CREATE TABLE tier_upgrades (
  upgrade_id VARCHAR(50) PRIMARY KEY,
  installation_id VARCHAR(16) NOT NULL,

  from_tier INTEGER NOT NULL,
  to_tier INTEGER NOT NULL,

  upgrade_method VARCHAR(20) NOT NULL CHECK (upgrade_method IN ('payment', 'promo_code', 'manual', 'opencpn_detect')),
  subscription_id VARCHAR(50) NULL,
  payment_id VARCHAR(50) NULL,

  user_email VARCHAR(255),
  user_name VARCHAR(255),

  upgraded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_installation_id (installation_id),
  INDEX idx_upgraded_at (upgraded_at),
  FOREIGN KEY (installation_id) REFERENCES installations(installation_id),
  FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id),
  FOREIGN KEY (payment_id) REFERENCES payments(payment_id)
);
```

**Update existing `installations` table:**
```sql
ALTER TABLE installations
ADD COLUMN is_paid_tier BOOLEAN DEFAULT FALSE,
ADD COLUMN subscription_status VARCHAR(20) CHECK (subscription_status IN ('none', 'active', 'past_due', 'canceled', 'expired')),
ADD COLUMN subscription_expires_at TIMESTAMP NULL;
```

**Why 2-3 hours?**
- Write SQL schema
- Create migration scripts
- Test locally
- Handle foreign keys and indexes
- Document table relationships

---

#### 2.2 Stripe Webhook Handler (4-6 hours)

**File:** `/opt/d3kos/services/billing/stripe_webhook_handler.py`

This is the CORE of the integration. When Stripe events happen, this handler:
1. Receives webhook POST request
2. Verifies signature (security)
3. Processes event
4. Updates database
5. Triggers tier upgrade/downgrade

**Implementation:**

```python
#!/usr/bin/env python3
"""
Stripe Webhook Handler for d3kOS
Processes subscription events from Stripe
"""

import os
import json
import stripe
from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Load Stripe API key from environment
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'd3kos'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME', 'd3kos_central')
    )

@app.route('/api/v1/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle the event
    event_type = event['type']
    event_data = event['data']['object']

    print(f"Received Stripe webhook: {event_type}")

    if event_type == 'customer.subscription.created':
        handle_subscription_created(event_data)

    elif event_type == 'customer.subscription.updated':
        handle_subscription_updated(event_data)

    elif event_type == 'customer.subscription.deleted':
        handle_subscription_deleted(event_data)

    elif event_type == 'invoice.payment_succeeded':
        handle_payment_succeeded(event_data)

    elif event_type == 'invoice.payment_failed':
        handle_payment_failed(event_data)

    elif event_type == 'customer.subscription.trial_will_end':
        handle_trial_ending(event_data)

    else:
        print(f"Unhandled event type: {event_type}")

    return jsonify({'received': True}), 200


def handle_subscription_created(subscription_data):
    """Handle new subscription creation"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Extract subscription details
    subscription_id = subscription_data['id']
    customer_id = subscription_data['customer']
    status = subscription_data['status']

    # Get installation_id from subscription metadata
    installation_id = subscription_data['metadata'].get('installation_id')
    if not installation_id:
        print(f"ERROR: No installation_id in subscription metadata")
        return

    # Get price information
    price_data = subscription_data['items']['data'][0]['price']
    amount_cents = price_data['unit_amount']
    currency = price_data['currency'].upper()
    billing_interval = price_data['recurring']['interval']

    # Determine tier from amount
    tier = 2 if amount_cents == 999 else 3

    # Get customer email
    customer = stripe.Customer.retrieve(customer_id)
    user_email = customer.get('email')
    user_name = customer.get('name')

    # Get billing dates
    current_period_start = datetime.fromtimestamp(subscription_data['current_period_start'])
    current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])

    # Insert subscription record
    cursor.execute("""
        INSERT INTO subscriptions (
            subscription_id, installation_id, tier, status,
            payment_provider, provider_subscription_id, provider_customer_id,
            started_at, current_period_start, current_period_end,
            amount_cents, currency, billing_interval,
            user_email, user_name
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            status = VALUES(status),
            current_period_start = VALUES(current_period_start),
            current_period_end = VALUES(current_period_end),
            updated_at = CURRENT_TIMESTAMP
    """, (
        subscription_id, installation_id, tier, status,
        'stripe', subscription_id, customer_id,
        datetime.now(), current_period_start, current_period_end,
        amount_cents, currency, billing_interval,
        user_email, user_name
    ))

    # Update installations table
    cursor.execute("""
        UPDATE installations
        SET tier = %s,
            is_paid_tier = TRUE,
            subscription_status = %s,
            subscription_expires_at = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE installation_id = %s
    """, (tier, status, current_period_end, installation_id))

    # Log tier upgrade
    cursor.execute("""
        INSERT INTO tier_upgrades (
            upgrade_id, installation_id, from_tier, to_tier,
            upgrade_method, subscription_id, user_email, user_name
        ) VALUES (UUID(), %s, 1, %s, 'payment', %s, %s, %s)
    """, (installation_id, tier, subscription_id, user_email, user_name))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Subscription created: {installation_id} → Tier {tier}")

    # TODO: Send push notification to mobile app
    # send_mobile_notification(installation_id, "Subscription activated!")


def handle_subscription_updated(subscription_data):
    """Handle subscription updates (status changes, plan changes)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    subscription_id = subscription_data['id']
    status = subscription_data['status']

    current_period_start = datetime.fromtimestamp(subscription_data['current_period_start'])
    current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])

    canceled_at = None
    if subscription_data.get('canceled_at'):
        canceled_at = datetime.fromtimestamp(subscription_data['canceled_at'])

    # Update subscription record
    cursor.execute("""
        UPDATE subscriptions
        SET status = %s,
            current_period_start = %s,
            current_period_end = %s,
            canceled_at = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE provider_subscription_id = %s
    """, (status, current_period_start, current_period_end, canceled_at, subscription_id))

    # Update installations table
    cursor.execute("""
        UPDATE installations i
        JOIN subscriptions s ON i.installation_id = s.installation_id
        SET i.subscription_status = %s,
            i.subscription_expires_at = %s,
            i.updated_at = CURRENT_TIMESTAMP
        WHERE s.provider_subscription_id = %s
    """, (status, current_period_end, subscription_id))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Subscription updated: {subscription_id} → Status: {status}")


def handle_subscription_deleted(subscription_data):
    """Handle subscription cancellation/expiration"""
    conn = get_db_connection()
    cursor = conn.cursor()

    subscription_id = subscription_data['id']

    # Get installation_id
    cursor.execute("SELECT installation_id FROM subscriptions WHERE provider_subscription_id = %s", (subscription_id,))
    result = cursor.fetchone()
    if not result:
        print(f"ERROR: Subscription not found: {subscription_id}")
        return

    installation_id = result[0]

    # Update subscription status
    cursor.execute("""
        UPDATE subscriptions
        SET status = 'expired',
            expires_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE provider_subscription_id = %s
    """, (subscription_id,))

    # Downgrade tier to 1
    cursor.execute("""
        UPDATE installations
        SET tier = 1,
            is_paid_tier = FALSE,
            subscription_status = 'expired',
            updated_at = CURRENT_TIMESTAMP
        WHERE installation_id = %s
    """, (installation_id,))

    # Log tier downgrade
    cursor.execute("""
        INSERT INTO tier_upgrades (
            upgrade_id, installation_id, from_tier, to_tier,
            upgrade_method, subscription_id
        ) VALUES (UUID(), %s, 2, 1, 'payment', %s)
    """, (installation_id, subscription_id))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"⚠️ Subscription expired: {installation_id} → Downgraded to Tier 1")

    # TODO: Send email notification
    # send_email_notification(installation_id, "Subscription expired")


def handle_payment_succeeded(invoice_data):
    """Handle successful payment"""
    conn = get_db_connection()
    cursor = conn.cursor()

    invoice_id = invoice_data['id']
    subscription_id = invoice_data['subscription']
    amount_cents = invoice_data['amount_paid']
    currency = invoice_data['currency'].upper()

    payment_intent_id = invoice_data.get('payment_intent')
    paid_at = datetime.fromtimestamp(invoice_data['status_transitions']['paid_at'])

    # Get installation_id
    cursor.execute("SELECT installation_id FROM subscriptions WHERE provider_subscription_id = %s", (subscription_id,))
    result = cursor.fetchone()
    if not result:
        print(f"ERROR: Subscription not found for invoice: {invoice_id}")
        return

    installation_id = result[0]

    # Insert payment record
    cursor.execute("""
        INSERT INTO payments (
            payment_id, installation_id, subscription_id,
            provider_payment_id, amount_cents, currency,
            status, invoice_url, receipt_url, paid_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        payment_intent_id or invoice_id,
        installation_id,
        subscription_id,
        payment_intent_id or invoice_id,
        amount_cents,
        currency,
        'succeeded',
        invoice_data.get('hosted_invoice_url'),
        invoice_data.get('invoice_pdf'),
        paid_at
    ))

    # Reset payment failure counter
    cursor.execute("""
        UPDATE subscriptions
        SET payment_failed_count = 0,
            last_payment_at = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE provider_subscription_id = %s
    """, (paid_at, subscription_id))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Payment succeeded: {installation_id} - ${amount_cents/100:.2f}")


def handle_payment_failed(invoice_data):
    """Handle failed payment (start grace period)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    invoice_id = invoice_data['id']
    subscription_id = invoice_data['subscription']

    # Get installation_id
    cursor.execute("SELECT installation_id, payment_failed_count FROM subscriptions WHERE provider_subscription_id = %s", (subscription_id,))
    result = cursor.fetchone()
    if not result:
        print(f"ERROR: Subscription not found for invoice: {invoice_id}")
        return

    installation_id, failed_count = result
    failed_count += 1

    # Update subscription
    cursor.execute("""
        UPDATE subscriptions
        SET payment_failed_count = %s,
            status = 'past_due',
            updated_at = CURRENT_TIMESTAMP
        WHERE provider_subscription_id = %s
    """, (failed_count, subscription_id))

    # Update installations
    cursor.execute("""
        UPDATE installations
        SET subscription_status = 'past_due',
            updated_at = CURRENT_TIMESTAMP
        WHERE installation_id = %s
    """, (installation_id,))

    # Insert failed payment record
    cursor.execute("""
        INSERT INTO payments (
            payment_id, installation_id, subscription_id,
            provider_payment_id, amount_cents, currency,
            status, failure_reason
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        invoice_id,
        installation_id,
        subscription_id,
        invoice_id,
        invoice_data['amount_due'],
        invoice_data['currency'].upper(),
        'failed',
        invoice_data.get('last_finalization_error', {}).get('message')
    ))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"⚠️ Payment failed: {installation_id} (Attempt {failed_count}/4)")

    # TODO: Send email warning
    # send_email_warning(installation_id, failed_count)


def handle_trial_ending(subscription_data):
    """Handle trial ending soon (3 days before)"""
    subscription_id = subscription_data['id']
    trial_end = datetime.fromtimestamp(subscription_data['trial_end'])

    print(f"📅 Trial ending soon: {subscription_id} on {trial_end}")

    # TODO: Send reminder email
    # send_trial_ending_email(subscription_id, trial_end)


if __name__ == '__main__':
    # Run webhook handler
    app.run(host='0.0.0.0', port=5000)
```

**Why 4-6 hours?**
- Write Python Flask app (~2 hours)
- Implement each webhook handler (~3 hours)
- Test with Stripe CLI (~1 hour)
- Error handling and logging
- Security (signature verification)

---

#### 2.3 Subscription Management API (4-6 hours)

Mobile app needs endpoints to:
- Check current tier status
- Get subscription details
- Cancel subscription
- Reactivate subscription
- Get payment history

**File:** `/opt/d3kos/services/billing/subscription_api.py`

```python
#!/usr/bin/env python3
"""
Subscription Management API for d3kOS
Provides endpoints for mobile app to manage subscriptions
"""

from flask import Flask, request, jsonify
import mysql.connector
import stripe
import os
from datetime import datetime

app = Flask(__name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'd3kos'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME', 'd3kos_central')
    )


@app.route('/api/v1/tier/status', methods=['GET'])
def get_tier_status():
    """Get current tier and subscription status for an installation"""
    installation_id = request.args.get('installation_id')

    if not installation_id:
        return jsonify({'error': 'installation_id required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get installation info
    cursor.execute("""
        SELECT i.tier, i.is_paid_tier, i.subscription_status, i.subscription_expires_at,
               s.subscription_id, s.payment_provider, s.billing_interval, s.amount_cents,
               s.current_period_end, s.canceled_at
        FROM installations i
        LEFT JOIN subscriptions s ON i.installation_id = s.installation_id AND s.status = 'active'
        WHERE i.installation_id = %s
    """, (installation_id,))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        return jsonify({'error': 'Installation not found'}), 404

    return jsonify({
        'installation_id': installation_id,
        'tier': result['tier'],
        'is_paid_tier': result['is_paid_tier'],
        'subscription_status': result['subscription_status'],
        'subscription_expires_at': result['subscription_expires_at'].isoformat() if result['subscription_expires_at'] else None,
        'subscription': {
            'id': result['subscription_id'],
            'provider': result['payment_provider'],
            'interval': result['billing_interval'],
            'amount': result['amount_cents'] / 100 if result['amount_cents'] else None,
            'next_billing_date': result['current_period_end'].isoformat() if result['current_period_end'] else None,
            'canceled': result['canceled_at'] is not None
        } if result['subscription_id'] else None
    }), 200


@app.route('/api/v1/stripe/checkout/session', methods=['POST'])
def create_checkout_session():
    """Create Stripe Checkout Session for mobile app"""
    data = request.get_json()

    installation_id = data.get('installation_id')
    tier = data.get('tier')  # 2 or 3
    billing_interval = data.get('billing_interval', 'month')  # 'month' or 'year'

    if not installation_id or not tier:
        return jsonify({'error': 'installation_id and tier required'}), 400

    # Determine price ID
    if tier == 2 and billing_interval == 'month':
        price_id = 'price_tier2_monthly_999'
    elif tier == 3 and billing_interval == 'year':
        price_id = 'price_tier3_annual_9999'
    else:
        return jsonify({'error': 'Invalid tier/interval combination'}), 400

    try:
        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url='d3kos://subscription/success',
            cancel_url='d3kos://subscription/canceled',
            metadata={
                'installation_id': installation_id,
                'tier': tier
            },
            subscription_data={
                'metadata': {
                    'installation_id': installation_id
                }
            }
        )

        return jsonify({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/subscription/cancel', methods=['POST'])
def cancel_subscription():
    """Cancel active subscription"""
    data = request.get_json()
    installation_id = data.get('installation_id')

    if not installation_id:
        return jsonify({'error': 'installation_id required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get active subscription
    cursor.execute("""
        SELECT subscription_id, payment_provider, provider_subscription_id
        FROM subscriptions
        WHERE installation_id = %s AND status = 'active'
    """, (installation_id,))

    result = cursor.fetchone()

    if not result:
        cursor.close()
        conn.close()
        return jsonify({'error': 'No active subscription found'}), 404

    # Cancel based on provider
    if result['payment_provider'] == 'stripe':
        try:
            # Cancel at period end (user keeps access until then)
            stripe.Subscription.modify(
                result['provider_subscription_id'],
                cancel_at_period_end=True
            )

            # Update database
            cursor.execute("""
                UPDATE subscriptions
                SET canceled_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE subscription_id = %s
            """, (result['subscription_id'],))

            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({
                'message': 'Subscription will cancel at end of billing period',
                'canceled_at': datetime.now().isoformat()
            }), 200

        except Exception as e:
            cursor.close()
            conn.close()
            return jsonify({'error': str(e)}), 500

    else:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Provider not supported yet'}), 400


@app.route('/api/v1/subscription/reactivate', methods=['POST'])
def reactivate_subscription():
    """Reactivate canceled subscription (before it expires)"""
    data = request.get_json()
    installation_id = data.get('installation_id')

    if not installation_id:
        return jsonify({'error': 'installation_id required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get canceled subscription
    cursor.execute("""
        SELECT subscription_id, payment_provider, provider_subscription_id
        FROM subscriptions
        WHERE installation_id = %s AND status = 'active' AND canceled_at IS NOT NULL
    """, (installation_id,))

    result = cursor.fetchone()

    if not result:
        cursor.close()
        conn.close()
        return jsonify({'error': 'No canceled subscription found'}), 404

    if result['payment_provider'] == 'stripe':
        try:
            # Remove cancel_at_period_end flag
            stripe.Subscription.modify(
                result['provider_subscription_id'],
                cancel_at_period_end=False
            )

            # Update database
            cursor.execute("""
                UPDATE subscriptions
                SET canceled_at = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE subscription_id = %s
            """, (result['subscription_id'],))

            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({
                'message': 'Subscription reactivated',
                'status': 'active'
            }), 200

        except Exception as e:
            cursor.close()
            conn.close()
            return jsonify({'error': str(e)}), 500

    else:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Provider not supported yet'}), 400


@app.route('/api/v1/subscription/history', methods=['GET'])
def get_payment_history():
    """Get payment history for an installation"""
    installation_id = request.args.get('installation_id')

    if not installation_id:
        return jsonify({'error': 'installation_id required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT payment_id, amount_cents, currency, status, paid_at, invoice_url
        FROM payments
        WHERE installation_id = %s
        ORDER BY paid_at DESC
        LIMIT 50
    """, (installation_id,))

    payments = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({
        'installation_id': installation_id,
        'payments': [{
            'id': p['payment_id'],
            'amount': p['amount_cents'] / 100,
            'currency': p['currency'],
            'status': p['status'],
            'date': p['paid_at'].isoformat() if p['paid_at'] else None,
            'invoice_url': p['invoice_url']
        } for p in payments]
    }), 200


@app.route('/api/v1/stripe/customer-portal', methods=['GET'])
def get_customer_portal_url():
    """Get Stripe Customer Portal URL for subscription management"""
    installation_id = request.args.get('installation_id')

    if not installation_id:
        return jsonify({'error': 'installation_id required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get customer ID
    cursor.execute("""
        SELECT provider_customer_id
        FROM subscriptions
        WHERE installation_id = %s AND payment_provider = 'stripe'
        ORDER BY created_at DESC
        LIMIT 1
    """, (installation_id,))

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        return jsonify({'error': 'No Stripe customer found'}), 404

    try:
        # Create portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=result['provider_customer_id'],
            return_url='d3kos://subscription/portal-return',
        )

        return jsonify({
            'portal_url': portal_session.url
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

**Why 4-6 hours?**
- Write API endpoints (~3 hours)
- Stripe API integration (~2 hours)
- Database queries and transactions
- Error handling
- API documentation

---

#### 2.4 Systemd Services (1-2 hours)

Create services to auto-start webhook handler and API:

**File:** `/etc/systemd/system/d3kos-stripe-webhook.service`
```ini
[Unit]
Description=d3kOS Stripe Webhook Handler
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/billing
ExecStart=/usr/bin/python3 /opt/d3kos/services/billing/stripe_webhook_handler.py
Restart=always
RestartSec=10

Environment="STRIPE_SECRET_KEY=sk_live_..."
Environment="STRIPE_WEBHOOK_SECRET=whsec_..."
Environment="DB_HOST=localhost"
Environment="DB_USER=d3kos"
Environment="DB_PASSWORD=..."
Environment="DB_NAME=d3kos_central"

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**File:** `/etc/systemd/system/d3kos-subscription-api.service`
```ini
[Unit]
Description=d3kOS Subscription Management API
After=network.target mysql.service
Wants=mysql.service

[Service]
Type=simple
User=d3kos
WorkingDirectory=/opt/d3kos/services/billing
ExecStart=/usr/bin/python3 /opt/d3kos/services/billing/subscription_api.py
Restart=always
RestartSec=10

Environment="STRIPE_SECRET_KEY=sk_live_..."
Environment="DB_HOST=localhost"
Environment="DB_USER=d3kos"
Environment="DB_PASSWORD=..."
Environment="DB_NAME=d3kos_central"

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable d3kos-stripe-webhook.service
sudo systemctl enable d3kos-subscription-api.service
sudo systemctl start d3kos-stripe-webhook.service
sudo systemctl start d3kos-subscription-api.service
```

---

#### 2.5 Nginx Reverse Proxy (1 hour)

Configure Nginx to proxy webhook and API endpoints:

**File:** `/etc/nginx/sites-enabled/d3kos-billing`
```nginx
# Stripe Webhook Handler
upstream stripe_webhook {
    server localhost:5000;
}

# Subscription API
upstream subscription_api {
    server localhost:5001;
}

server {
    listen 443 ssl http2;
    server_name api.d3kos.com;

    ssl_certificate /etc/letsencrypt/live/api.d3kos.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.d3kos.com/privkey.pem;

    # Stripe webhook endpoint
    location /api/v1/webhooks/stripe {
        proxy_pass http://stripe_webhook/api/v1/webhooks/stripe;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Important: Preserve raw body for signature verification
        proxy_set_header Content-Type $content_type;
        proxy_buffering off;
    }

    # Subscription management endpoints
    location /api/v1/tier/ {
        proxy_pass http://subscription_api/api/v1/tier/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/v1/stripe/ {
        proxy_pass http://subscription_api/api/v1/stripe/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/v1/subscription/ {
        proxy_pass http://subscription_api/api/v1/subscription/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

#### 2.6 Environment Variables & Secrets (1 hour)

Securely store API keys:

**File:** `/opt/d3kos/config/.env.billing`
```bash
# Stripe API Keys (get from Stripe Dashboard)
STRIPE_SECRET_KEY=sk_live_51AbCdEf...
STRIPE_PUBLISHABLE_KEY=pk_live_51AbCdEf...
STRIPE_WEBHOOK_SECRET=whsec_12345...

# Database
DB_HOST=localhost
DB_USER=d3kos_billing
DB_PASSWORD=CHANGE_THIS_PASSWORD
DB_NAME=d3kos_central
DB_PORT=3306

# API URLs
API_BASE_URL=https://api.d3kos.com
WEBHOOK_URL=https://api.d3kos.com/api/v1/webhooks/stripe

# Email (for notifications)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.xyz...
FROM_EMAIL=noreply@d3kos.com
```

Set permissions:
```bash
chmod 600 /opt/d3kos/config/.env.billing
chown d3kos:d3kos /opt/d3kos/config/.env.billing
```

---

### **Phase 3: Mobile App Integration (12-18 hours)**

This is where you integrate payment methods into iOS and Android apps.

#### 3.1 iOS App - Apple In-App Purchase Integration (6-9 hours)

**File:** `ios/d3kOS/SubscriptionManager.swift`

```swift
import StoreKit

@MainActor
class SubscriptionManager: ObservableObject {
    @Published var availableProducts: [Product] = []
    @Published var purchasedSubscriptions: [Product] = []
    @Published var subscriptionStatus: SubscriptionStatus?

    private let productIds = [
        "com.d3kos.tier2.monthly",
        "com.d3kos.tier3.annual"
    ]

    private var updates: Task<Void, Never>? = nil

    init() {
        updates = observeTransactionUpdates()
    }

    deinit {
        updates?.cancel()
    }

    // Load products from App Store
    func loadProducts() async {
        do {
            availableProducts = try await Product.products(for: productIds)
        } catch {
            print("Failed to load products: \\(error)")
        }
    }

    // Purchase a subscription
    func purchase(_ product: Product) async throws -> Transaction? {
        let result = try await product.purchase()

        switch result {
        case .success(let verification):
            let transaction = try checkVerified(verification)

            // Send receipt to backend
            await sendReceiptToBackend(transaction: transaction)

            // Finish transaction
            await transaction.finish()

            return transaction

        case .userCancelled:
            return nil

        case .pending:
            return nil

        @unknown default:
            return nil
        }
    }

    // Check verified transaction
    func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified:
            throw StoreError.failedVerification
        case .verified(let safe):
            return safe
        }
    }

    // Observe transaction updates
    func observeTransactionUpdates() -> Task<Void, Never> {
        Task(priority: .background) {
            for await verification in Transaction.updates {
                do {
                    let transaction = try checkVerified(verification)

                    // Send to backend
                    await sendReceiptToBackend(transaction: transaction)

                    await transaction.finish()
                } catch {
                    print("Transaction verification failed: \\(error)")
                }
            }
        }
    }

    // Send receipt to backend for verification
    func sendReceiptToBackend(transaction: Transaction) async {
        guard let installationId = UserDefaults.standard.string(forKey: "installation_id") else {
            print("No installation_id found")
            return
        }

        guard let receiptData = try? await getAppStoreReceipt() else {
            print("Failed to get receipt")
            return
        }

        let url = URL(string: "https://api.d3kos.com/api/v1/apple/verify-receipt")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body: [String: Any] = [
            "installation_id": installationId,
            "receipt_data": receiptData.base64EncodedString(),
            "transaction_id": String(transaction.id)
        ]

        request.httpBody = try? JSONSerialization.data(withJSONObject: body)

        do {
            let (data, response) = try await URLSession.shared.data(for: request)

            if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                print("✅ Receipt verified successfully")

                // Update local tier status
                await refreshSubscriptionStatus()
            } else {
                print("❌ Receipt verification failed")
            }
        } catch {
            print("Error sending receipt: \\(error)")
        }
    }

    // Get App Store receipt
    func getAppStoreReceipt() async throws -> Data {
        guard let receiptURL = Bundle.main.appStoreReceiptURL,
              let receiptData = try? Data(contentsOf: receiptURL) else {
            throw StoreError.noReceipt
        }
        return receiptData
    }

    // Refresh subscription status from backend
    func refreshSubscriptionStatus() async {
        guard let installationId = UserDefaults.standard.string(forKey: "installation_id") else {
            return
        }

        let url = URL(string: "https://api.d3kos.com/api/v1/tier/status?installation_id=\\(installationId)")!

        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            let status = try JSONDecoder().decode(SubscriptionStatus.self, from: data)

            DispatchQueue.main.async {
                self.subscriptionStatus = status
            }
        } catch {
            print("Error fetching subscription status: \\(error)")
        }
    }

    // Restore purchases
    func restorePurchases() async {
        do {
            try await AppStore.sync()
            print("✅ Purchases restored")
        } catch {
            print("❌ Failed to restore purchases: \\(error)")
        }
    }
}

// Models
struct SubscriptionStatus: Codable {
    let installationId: String
    let tier: Int
    let isPaidTier: Bool
    let subscriptionStatus: String?

    enum CodingKeys: String, CodingKey {
        case installationId = "installation_id"
        case tier
        case isPaidTier = "is_paid_tier"
        case subscriptionStatus = "subscription_status"
    }
}

enum StoreError: Error {
    case failedVerification
    case noReceipt
}
```

**SwiftUI View:**

```swift
import SwiftUI

struct SubscriptionView: View {
    @StateObject private var subscriptionManager = SubscriptionManager()
    @State private var isPurchasing = false

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Header
                Text("Upgrade to Premium")
                    .font(.title)
                    .fontWeight(.bold)

                // Current tier
                if let status = subscriptionManager.subscriptionStatus {
                    HStack {
                        Text("Current Tier:")
                        Spacer()
                        Text("Tier \\(status.tier)")
                            .fontWeight(.bold)
                    }
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(10)
                }

                // Products
                ForEach(subscriptionManager.availableProducts, id: \\.id) { product in
                    ProductCard(product: product) {
                        Task {
                            isPurchasing = true
                            do {
                                try await subscriptionManager.purchase(product)
                            } catch {
                                print("Purchase failed: \\(error)")
                            }
                            isPurchasing = false
                        }
                    }
                }

                // Restore purchases
                Button("Restore Purchases") {
                    Task {
                        await subscriptionManager.restorePurchases()
                    }
                }
                .foregroundColor(.blue)
            }
            .padding()
        }
        .task {
            await subscriptionManager.loadProducts()
            await subscriptionManager.refreshSubscriptionStatus()
        }
        .overlay {
            if isPurchasing {
                ProgressView("Processing...")
            }
        }
    }
}

struct ProductCard: View {
    let product: Product
    let onPurchase: () -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(product.displayName)
                .font(.headline)

            Text(product.description)
                .font(.subheadline)
                .foregroundColor(.gray)

            HStack {
                Text(product.displayPrice)
                    .font(.title2)
                    .fontWeight(.bold)

                Spacer()

                Button(action: onPurchase) {
                    Text("Subscribe")
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .padding(.horizontal, 20)
                        .padding(.vertical, 10)
                        .background(Color.blue)
                        .cornerRadius(8)
                }
            }
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(15)
        .overlay(
            RoundedRectangle(cornerRadius: 15)
                .stroke(Color.gray.opacity(0.2), lineWidth: 1)
        )
    }
}
```

**Why 6-9 hours for iOS?**
- Learn StoreKit 2 API (~2 hours if new to it)
- Implement purchase flow (~2 hours)
- Implement receipt validation (~2 hours)
- UI design and integration (~2 hours)
- Testing with Sandbox (~2 hours)

---

#### 3.2 Android App - Google Play Billing Integration (6-9 hours)

**File:** `android/app/src/main/java/com/d3kos/SubscriptionManager.kt`

```kotlin
package com.d3kos

import android.app.Activity
import android.content.Context
import com.android.billingclient.api.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

class SubscriptionManager(private val context: Context) {

    private var billingClient: BillingClient
    private val productIds = listOf("tier2_monthly", "tier3_annual")

    init {
        billingClient = BillingClient.newBuilder(context)
            .setListener { billingResult, purchases ->
                if (billingResult.responseCode == BillingClient.BillingResponseCode.OK && purchases != null) {
                    for (purchase in purchases) {
                        handlePurchase(purchase)
                    }
                }
            }
            .enablePendingPurchases()
            .build()

        startConnection()
    }

    private fun startConnection() {
        billingClient.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(billingResult: BillingResult) {
                if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                    // Connected successfully
                    queryProducts()
                }
            }

            override fun onBillingServiceDisconnected() {
                // Retry connection
                startConnection()
            }
        })
    }

    suspend fun queryProducts(): List<ProductDetails> = withContext(Dispatchers.IO) {
        val productList = productIds.map {
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(it)
                .setProductType(BillingClient.ProductType.SUBS)
                .build()
        }

        val params = QueryProductDetailsParams.newBuilder()
            .setProductList(productList)
            .build()

        val productDetailsResult = billingClient.queryProductDetails(params)

        if (productDetailsResult.billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
            productDetailsResult.productDetailsList ?: emptyList()
        } else {
            emptyList()
        }
    }

    fun launchPurchaseFlow(activity: Activity, productDetails: ProductDetails) {
        val offerToken = productDetails.subscriptionOfferDetails?.get(0)?.offerToken ?: return

        val productDetailsParamsList = listOf(
            BillingFlowParams.ProductDetailsParams.newBuilder()
                .setProductDetails(productDetails)
                .setOfferToken(offerToken)
                .build()
        )

        val billingFlowParams = BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(productDetailsParamsList)
            .build()

        billingClient.launchBillingFlow(activity, billingFlowParams)
    }

    private fun handlePurchase(purchase: Purchase) {
        if (purchase.purchaseState == Purchase.PurchaseState.PURCHASED) {
            if (!purchase.isAcknowledged) {
                // Verify with backend
                verifyPurchaseWithBackend(purchase) { success ->
                    if (success) {
                        // Acknowledge purchase
                        acknowledgePurchase(purchase)
                    }
                }
            }
        }
    }

    private fun acknowledgePurchase(purchase: Purchase) {
        val acknowledgePurchaseParams = AcknowledgePurchaseParams.newBuilder()
            .setPurchaseToken(purchase.purchaseToken)
            .build()

        billingClient.acknowledgePurchase(acknowledgePurchaseParams) { billingResult ->
            if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                println("✅ Purchase acknowledged")
            }
        }
    }

    private fun verifyPurchaseWithBackend(purchase: Purchase, callback: (Boolean) -> Unit) {
        val installationId = getInstallationId() ?: return callback(false)

        val client = OkHttpClient()
        val url = "https://api.d3kos.com/api/v1/google/verify-purchase"

        val json = JSONObject().apply {
            put("installation_id", installationId)
            put("purchase_token", purchase.purchaseToken)
            put("product_id", purchase.products[0])
        }

        val body = json.toString().toRequestBody("application/json".toMediaType())

        val request = Request.Builder()
            .url(url)
            .post(body)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                println("❌ Failed to verify purchase: ${e.message}")
                callback(false)
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    println("✅ Purchase verified successfully")
                    callback(true)
                } else {
                    println("❌ Purchase verification failed")
                    callback(false)
                }
            }
        })
    }

    suspend fun restorePurchases(): List<Purchase> = withContext(Dispatchers.IO) {
        val params = QueryPurchasesParams.newBuilder()
            .setProductType(BillingClient.ProductType.SUBS)
            .build()

        val purchasesResult = billingClient.queryPurchasesAsync(params)

        if (purchasesResult.billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
            purchasesResult.purchasesList
        } else {
            emptyList()
        }
    }

    private fun getInstallationId(): String? {
        val prefs = context.getSharedPreferences("d3kos", Context.MODE_PRIVATE)
        return prefs.getString("installation_id", null)
    }
}
```

**Jetpack Compose UI:**

```kotlin
@Composable
fun SubscriptionScreen(subscriptionManager: SubscriptionManager) {
    val scope = rememberCoroutineScope()
    var products by remember { mutableStateOf<List<ProductDetails>>(emptyList()) }
    var isPurchasing by remember { mutableStateOf(false) }
    val context = LocalContext.current
    val activity = context as Activity

    LaunchedEffect(Unit) {
        products = subscriptionManager.queryProducts()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Text(
            text = "Upgrade to Premium",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(16.dp))

        products.forEach { product ->
            ProductCard(
                product = product,
                onPurchase = {
                    isPurchasing = true
                    subscriptionManager.launchPurchaseFlow(activity, product)
                    isPurchasing = false
                }
            )
            Spacer(modifier = Modifier.height(12.dp))
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(
            onClick = {
                scope.launch {
                    subscriptionManager.restorePurchases()
                }
            }
        ) {
            Text("Restore Purchases")
        }
    }

    if (isPurchasing) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            CircularProgressIndicator()
        }
    }
}

@Composable
fun ProductCard(product: ProductDetails, onPurchase: () -> Unit) {
    val offer = product.subscriptionOfferDetails?.get(0)
    val price = offer?.pricingPhases?.pricingPhaseList?.get(0)?.formattedPrice ?: ""

    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = product.name,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )

            Text(
                text = product.description,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = price,
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold
                )

                Button(onClick = onPurchase) {
                    Text("Subscribe")
                }
            }
        }
    }
}
```

**Why 6-9 hours for Android?**
- Learn Google Play Billing Library (~2 hours if new to it)
- Implement purchase flow (~2 hours)
- Implement purchase verification (~2 hours)
- UI design and integration (~2 hours)
- Testing with test accounts (~2 hours)

---

### **Phase 4: Testing & Deployment (8-12 hours)**

#### 4.1 Local Testing (3-4 hours)

**Stripe CLI Testing:**
```bash
# Terminal 1: Start webhook handler
python3 /opt/d3kos/services/billing/stripe_webhook_handler.py

# Terminal 2: Forward Stripe webhooks
stripe listen --forward-to localhost:5000/api/v1/webhooks/stripe

# Terminal 3: Trigger test events
stripe trigger customer.subscription.created
stripe trigger invoice.payment_succeeded
stripe trigger invoice.payment_failed
stripe trigger customer.subscription.deleted
```

**Test Scenarios:**
1. ✅ Create subscription → Verify tier upgraded to 2
2. ✅ Successful payment → Verify payment record created
3. ✅ Failed payment → Verify grace period activated
4. ✅ Cancel subscription → Verify tier remains until expiration
5. ✅ Subscription expires → Verify tier downgraded to 1

---

#### 4.2 iOS Sandbox Testing (2-3 hours)

1. Create Sandbox test accounts in App Store Connect
2. Test purchase flow with test account
3. Verify receipt validation
4. Test subscription renewal (accelerated in sandbox)
5. Test subscription cancellation
6. Test restore purchases

---

#### 4.3 Android Testing (2-3 hours)

1. Create license testing account in Google Play Console
2. Upload app to Internal Testing track
3. Test purchase flow
4. Verify purchase validation
5. Test subscription renewal
6. Test subscription cancellation
7. Test restore purchases

---

#### 4.4 Production Deployment (1-2 hours)

1. Switch Stripe to production mode
2. Update environment variables with live API keys
3. Deploy backend services to production server
4. Configure production webhook URL in Stripe
5. Submit iOS app to App Store for review
6. Submit Android app to Google Play for review
7. Monitor logs for errors
8. Set up uptime monitoring (UptimeRobot, Pingdom)

---

## Ongoing Maintenance

**Monthly Tasks (1-2 hours/month):**
- Monitor webhook delivery success rate
- Review failed payments and grace period expirations
- Handle customer support inquiries
- Review Stripe dashboard for anomalies
- Update payment gateway API if Stripe releases breaking changes

**Quarterly Tasks (2-3 hours/quarter):**
- Review subscription churn rate
- Analyze payment failure patterns
- Optimize pricing/billing intervals
- Update mobile app for OS changes

---

## Total Time Summary

| Phase | Minimum | Maximum | Average |
|-------|---------|---------|---------|
| Phase 1: Stripe Setup | 4 hours | 6 hours | 5 hours |
| Phase 2: Backend API | 16 hours | 24 hours | 20 hours |
| Phase 3: Mobile App Integration | 12 hours | 18 hours | 15 hours |
| Phase 4: Testing & Deployment | 8 hours | 12 hours | 10 hours |
| **TOTAL** | **40 hours** | **60 hours** | **50 hours** |

---

## Cost Breakdown

**Development Costs:**
- Developer time: 40-60 hours × $50-150/hour = $2,000 - $9,000

**Monthly Operational Costs:**
- Stripe fees: 2.9% + $0.30 per transaction
- Apple IAP fees: 15-30% (deducted by Apple)
- Google Play fees: 15-30% (deducted by Google)
- Server hosting: $10-50/month
- Email notifications: $0-10/month (SendGrid free tier)

**Example Revenue Calculation:**

If you have 100 Tier 2 subscribers ($9.99/month):
- Gross revenue: $999/month
- Stripe fees (if used): ~$30/month
- Apple IAP fees (30%): ~$300/month (if all iOS)
- Google Play fees (15-30%): ~$150-300/month (if all Android)
- Net revenue: $369-619/month (depending on platform mix)

**Break-even:** ~4-15 months depending on development costs

---

## Key Takeaways

1. **Stripe is a tool, not a complete solution**
   - You must build backend, mobile integration, and database
   - Estimated 40-60 hours of development work

2. **Apple and Google fees are mandatory**
   - 15-30% commission on all in-app purchases
   - Cannot be avoided if distributing via App Store/Play Store

3. **Testing is critical**
   - Use Stripe test mode extensively
   - Test iOS Sandbox and Android Internal Testing thoroughly
   - Production testing with small user group first

4. **Ongoing maintenance required**
   - Monitor webhooks, handle failed payments, customer support
   - Budget 1-3 hours/month for maintenance

5. **Alternatives to consider**
   - If budget is tight: Start with Stripe-only (web subscriptions), add IAP later
   - If no mobile app yet: Stripe-only is sufficient
   - If enterprise focus: Consider custom invoicing instead of subscriptions

---

## Next Steps

1. Read MASTER_SYSTEM_SPEC Section 6.3.4 (now updated with full details)
2. Review code samples above
3. Set up Stripe test account
4. Create database schema
5. Start with Phase 1 (Stripe setup)
6. Build backend webhook handler (Phase 2)
7. Integrate mobile apps (Phase 3)
8. Test thoroughly (Phase 4)
9. Deploy to production

---

**Last Updated:** February 16, 2026
**Document Version:** 1.0
