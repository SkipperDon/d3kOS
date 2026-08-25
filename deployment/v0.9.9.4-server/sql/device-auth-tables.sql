-- device-auth-tables.sql
-- BUG-66 Phase A — d3kOS device enrolment and registration tables
-- Source: D3KOS_DEVICE_REGISTRATION_SPEC.md §6 (verbatim)
--
-- These tables are created automatically via the plugin activation hook in
-- d3kos-device-auth.php (using dbDelta). This file is the reference schema
-- and can be used to create tables manually via phpMyAdmin if needed.
--
-- Table names do NOT use the WordPress prefix — they use the amboat_ namespace
-- directly, consistent with the existing amboat_devices table in version-heartbeat.php.
-- If running manually, verify this matches your WordPress table naming convention.

CREATE TABLE IF NOT EXISTS amboat_device_enrolments (
  device_token     VARCHAR(36)   PRIMARY KEY,
  public_key       VARBINARY(32) NOT NULL,       -- Ed25519 raw public key (32 bytes)
  status           ENUM('pending','approved','rejected','blocked') NOT NULL DEFAULT 'pending',
  contact_email    VARCHAR(254)  NULL,
  enrol_note       TEXT          NULL,
  enrolled_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  enrolled_ip      VARBINARY(16) NULL,            -- inet_pton result (IPv4 or IPv6)
  reviewed_at      TIMESTAMP     NULL,
  reviewed_by      BIGINT        NULL,
  INDEX (status),
  INDEX (contact_email)
);

CREATE TABLE IF NOT EXISTS amboat_registration_codes (
  code_hash        CHAR(64)      PRIMARY KEY,     -- SHA256 of the issued code (plaintext never stored)
  device_token     VARCHAR(36)   NOT NULL,
  issued_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at       TIMESTAMP     NOT NULL,        -- server-clocked (15 min from issued_at)
  status           ENUM('valid','used','superseded') NOT NULL DEFAULT 'valid',
  used_at          TIMESTAMP     NULL,
  used_by_user_id  BIGINT        NULL,
  FOREIGN KEY (device_token) REFERENCES amboat_device_enrolments(device_token),
  INDEX (device_token, status),
  INDEX (expires_at)
);

CREATE TABLE IF NOT EXISTS amboat_device_accounts (
  device_token     VARCHAR(36)   PRIMARY KEY,     -- D4: exactly 1 account per device
  user_id          BIGINT        NOT NULL UNIQUE,
  created_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX (user_id)
);

CREATE TABLE IF NOT EXISTS amboat_registration_audit (
  id           BIGINT AUTO_INCREMENT PRIMARY KEY,
  event        ENUM('enrol','approve','reject','block','code_issued',
                    'redeem_ok','redeem_fail','rate_limited') NOT NULL,
  device_token VARCHAR(36)   NULL,
  user_id      BIGINT        NULL,
  ip           VARBINARY(16) NULL,
  detail       VARCHAR(255)  NULL,
  created_at   TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX (device_token),
  INDEX (created_at),
  INDEX (event)
);
