# Privacy Policy — AtMyBoat.com
**Effective date:** [INSERT DATE]
**Last updated:** [INSERT DATE]

---

## 1. Who We Are

AtMyBoat.com ("we", "us", "our") is operated by Donald Moskaluk as a sole proprietorship. We provide the d3kOS marine operating system, the AtMyBoat PWA companion app, and related services for recreational boaters.

Contact: skipperdon@atmyboat.com

---

## 2. What Data We Collect

### 2.1 Account Data
When you register an account, we collect:
- Email address
- Display name (you choose this)
- Registration date
- Subscription tier (T0–T3)

### 2.2 Device Data
When you pair a Pi device (d3kOS), we collect:
- A unique device identifier (UUID) generated on your device
- Vessel name (you choose this)
- Device software version
- Last-seen timestamp (when the device last connected)

### 2.3 Engine & Navigation Data
Your paired device sends the following data to our servers:
- Engine performance metrics (RPM, coolant temperature, battery voltage)
- GPS position (latitude/longitude) — used for fleet map features only
- Diagnostic information if you use the Fix My Pi feature

This data is associated with your device identifier, not your personal identity.

### 2.4 Support Communications
If you submit a support request, we collect:
- The message you write
- Your account tier and device status (to help diagnose issues)
- Email thread history

### 2.5 Billing Data
If you purchase a subscription, Stripe processes your payment. We store:
- Amount, currency, product, and payment date
- We do **not** store your credit card number

### 2.6 Usage Data
We do not use analytics trackers, advertising cookies, or third-party tracking scripts.

---

## 3. How We Use Your Data

| Purpose | Data Used | Legal Basis |
|---------|-----------|-------------|
| Provide the service (dashboard, PWA) | Account + device data | Contract performance |
| Respond to support requests | Account + device + message | Legitimate interest |
| Send support ticket updates | Email address | Contract performance |
| Process billing | Billing data via Stripe | Contract performance |
| Improve reliability (failure intelligence) | Anonymized error signatures | Legitimate interest |
| Comply with law | Billing records | Legal obligation |

We do **not** sell your data to third parties. We do not use your data for advertising.

---

## 4. Data Sharing

We share data with the following third parties only as necessary to provide the service:

| Party | Purpose | Location |
|-------|---------|----------|
| HostPapa | Web hosting and database | Canada |
| Stripe | Payment processing | United States |
| Google Gemini API | AI draft assist (support replies) | United States |

Data sent to Google Gemini for AI draft assist contains only: customer tier, device status summary, and active alert counts. **No email content, GPS coordinates, or personally identifying information is sent to Google.**

---

## 5. Your Rights

### GDPR (European Users) — Articles 15–22
You have the right to:
- **Access** your data — use "Download My Data" in the app Settings screen
- **Erasure** — use "Delete My Account" in the app Settings screen
- **Correction** — contact skipperdon@atmyboat.com to correct inaccurate data
- **Portability** — the data export is in JSON format, machine-readable
- **Objection** — contact us to object to any specific processing
- **Restriction** — contact us to request we restrict processing while a dispute is resolved

### CCPA (California Users)
You have the right to:
- Know what personal information we collect (see Section 2)
- Know whether your information is sold (it is not)
- Delete your personal information — use "Delete My Account" in Settings
- Non-discrimination for exercising these rights

### How to Exercise Rights
- **In-app:** Settings → Privacy & Data → Download My Data / Delete My Account
- **By email:** skipperdon@atmyboat.com — include "Privacy Request" in the subject line
- We will respond within 30 days

---

## 6. Data Retention

| Data Type | Retention Period |
|-----------|-----------------|
| Account data | Until account is deleted |
| Device & engine data | Until account is deleted or pairing is removed |
| Support tickets | Until account is deleted |
| Billing records | 7 years (legal/tax requirement — anonymized on account deletion) |
| Server logs | 30 days rolling |
| Deletion log | Permanent (contains only: a numeric user ID and deletion timestamp — no PII) |

---

## 7. Security

We protect your data using:
- HTTPS/TLS on all connections between the app, Pi device, and our servers
- Hashed authentication tokens (no plaintext passwords stored in our systems)
- Bearer token authentication on all API endpoints
- Database credentials never exposed to the public internet
- Regular security reviews as part of our software release process

We are a small operation. We do not have a dedicated security team. If you discover a vulnerability, please disclose it responsibly to skipperdon@atmyboat.com.

---

## 8. Cookies

The AtMyBoat PWA uses localStorage (not cookies) to store your session token on your device. No tracking cookies are set. No third-party cookies are loaded.

---

## 9. Children

AtMyBoat.com is not directed at children under 13. We do not knowingly collect data from children under 13.

---

## 10. Changes to This Policy

We will post updates to this page and update the "Last updated" date at the top. Material changes will be noted in the app.

---

## 11. Contact

Donald Moskaluk
AtMyBoat.com
skipperdon@atmyboat.com

*This policy is effective as of the date listed above.*
