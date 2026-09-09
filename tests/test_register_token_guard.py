"""
test_register_token_guard.py — BUG-111/114/119 server-side regression guards

Tests run as HTTP integration tests against HostPapa (live or staging).
Override the target URL with: REGISTER_URL=https://staging.example.com/register/

T9 and T10 and T14 can run against live (they use unique emails / invalid codes).
T11, T12, T13 require a controlled DB fixture — skipped by default.

Run: pytest tests/test_register_token_guard.py -v

Spec: deployment/docs/atomic-specs/BUG-111-118-REGISTRATION.md §8 Step 7 (T9–T14)
TDD status: T9 may pass now; T10/T14 expected to FAIL pre-fix (BUG-111).
"""

import os
import uuid
import pytest
import requests

REGISTER_URL = os.environ.get('REGISTER_URL', 'https://atmyboat.com/register/')
TIMEOUT = 15  # seconds


def unique_email():
    return f'test-reg-{uuid.uuid4().hex[:8]}@example-d3kos.invalid'


def post_registration(token: str, email: str = None) -> requests.Response:
    """POST to the registration page with given token and fields."""
    return requests.post(
        REGISTER_URL,
        data={
            'reg_token': token,
            'first_name': 'TestFirst',
            'last_name': 'TestLast',
            'email': email or unique_email(),
            'password': 'TempTestPass123!',
            'password_confirm': 'TempTestPass123!',
        },
        timeout=TIMEOUT,
        allow_redirects=True,
    )


# ---------------------------------------------------------------------------
# T9 — Empty reg_token + valid fields → account created, no code error
# Current: should already pass (empty token bypasses validation block)
# Expected: account created at T0, success screen shown
# ---------------------------------------------------------------------------
def test_T9_empty_token_creates_account():
    """POST with empty reg_token and valid fields must succeed without an error about invalid code."""
    resp = post_registration(token='', email=unique_email())
    assert resp.status_code == 200

    body = resp.text.lower()
    # Must not show a code-related error
    assert 'not valid' not in body, 'Empty token incorrectly triggered a code-format error'
    assert 'expired or already been used' not in body, 'Empty token incorrectly triggered expiry error'


# ---------------------------------------------------------------------------
# T10 — reg_token=R-CDEDWMH (present, malformed with R- prefix) → visible error, no account
# Current: FAILS — malformed token is silently ignored, account created anyway (BUG-111)
# Expected: error message visible, NO success screen, NO account created
# ---------------------------------------------------------------------------
def test_T10_malformed_token_with_prefix_shows_error():
    """POST with malformed token (R- prefix, 8 chars) must show error and NOT create an account."""
    resp = post_registration(token='R-CDEDWMH')
    assert resp.status_code == 200

    body = resp.text.lower()
    # Must NOT show success
    assert 'check your email' not in body, 'Malformed token wrongly created an account (BUG-111 still present)'
    # Must show an error about the code
    has_error = (
        'not valid' in body
        or 'registration code' in body
        or 'invalid' in body
        or 'error' in body
    )
    assert has_error, 'No error shown for malformed token R-CDEDWMH'


# ---------------------------------------------------------------------------
# T11 — Expired valid-format 7-char code → visible error, no account
# Skipped: requires staging DB with an expired token inserted as a fixture
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason='Requires staging DB with expired token fixture')
def test_T11_expired_code_shows_error():
    """POST with expired code must show error and not create account."""
    pass


# ---------------------------------------------------------------------------
# T12 — Already-used code → visible error, no account
# Skipped: requires staging DB with an already-used token as a fixture
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason='Requires staging DB with used token fixture')
def test_T12_used_code_shows_error():
    """POST with already-used code must show error and not create account."""
    pass


# ---------------------------------------------------------------------------
# T13 — Fresh valid code → account created, used_at set, Pi linked
# Skipped: requires staging DB with a fresh token pre-inserted as a fixture
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason='Requires staging DB with fresh token fixture — run manually with Pi online')
def test_T13_fresh_valid_code_creates_account():
    """POST with a fresh valid code must create an account and consume the token."""
    pass


# ---------------------------------------------------------------------------
# T14 — GET ?rt=R-CDEDWMH → R- prefix stripped, bare code pre-fills form, no format error
# Current: FAILS — R- prefix is NOT stripped; regex /^[A-Z2-9]{7}$/ rejects 'R-CDEDWMH';
#          the form may not pre-fill, and the bare code 'CDEDWMH' does not appear (BUG-114)
# Expected: bare code 'CDEDWMH' in a form field value; no banner about bad format
# ---------------------------------------------------------------------------
def test_T14_get_rt_param_strips_prefix_and_prefills_form():
    """GET /register/?rt=R-CDEDWMH must strip the R- prefix and pre-fill the form with CDEDWMH."""
    resp = requests.get(REGISTER_URL, params={'rt': 'R-CDEDWMH'}, timeout=TIMEOUT, allow_redirects=True)
    assert resp.status_code == 200

    body = resp.text
    # Bare code must appear (in a form field value or visible text)
    assert 'CDEDWMH' in body, 'Bare code CDEDWMH not found in response — R- prefix not stripped (BUG-114)'

    body_lower = body.lower()
    # No format-error message should appear just from a prefixed GET param
    assert 'invalid format' not in body_lower, 'Unexpected format-error banner on GET with R- prefix'
    assert 'not valid' not in body_lower, 'Unexpected code-error banner on GET with R- prefix'
