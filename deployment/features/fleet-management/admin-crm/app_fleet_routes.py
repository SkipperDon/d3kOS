import os
import io
import csv
import time
import math
from datetime import datetime, timedelta
from functools import wraps

import bcrypt
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify, Response)

from config import config
from db import test_connection, proxy_call
from email_client import fetch_inbox, fetch_message, send_reply, invalidate_cache
from ai_client import draft_reply
import local_db

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.permanent_session_lifetime = timedelta(hours=8)

local_db.init_db()

# Brute-force lockout: track failed attempts per IP
_failed_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 900  # 15 minutes

ALLOWED_TABLES = [
    "wpax_users", "wpax_usermeta", "d3kos_pairings",
    "amboat_devices", "amboat_billing", "amboat_command_queue",
    "amboat_alerts", "amboat_admin_log",
]


def _check_lockout(ip):
    now = time.time()
    attempts = _failed_attempts.get(ip, [])
    attempts = [t for t in attempts if now - t < LOCKOUT_SECONDS]
    _failed_attempts[ip] = attempts
    if len(attempts) >= MAX_ATTEMPTS:
        remaining = int(LOCKOUT_SECONDS - (now - attempts[0]))
        return True, max(remaining, 0)
    return False, 0


def _record_failure(ip):
    now = time.time()
    _failed_attempts.setdefault(ip, []).append(now)


def _clear_failures(ip):
    _failed_attempts.pop(ip, None)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        ip = request.remote_addr
        locked, remaining = _check_lockout(ip)
        if locked:
            error = f"Too many failed attempts. Try again in {remaining // 60}m {remaining % 60}s."
        else:
            password = request.form.get("password", "").encode("utf-8")
            stored_hash = config["admin_password_hash"].encode("utf-8")
            if bcrypt.checkpw(password, stored_hash):
                _clear_failures(ip)
                session.permanent = True
                session["logged_in"] = True
                return redirect(url_for("dashboard"))
            else:
                _record_failure(ip)
                locked, remaining = _check_lockout(ip)
                if locked:
                    error = f"Too many failed attempts. Locked for {LOCKOUT_SECONDS // 60} minutes."
                else:
                    attempts_left = MAX_ATTEMPTS - len(_failed_attempts.get(ip, []))
                    error = f"Incorrect password. {attempts_left} attempt(s) remaining."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.route("/")
@login_required
def dashboard():
    db_ok, db_err = test_connection()
    return render_template("dashboard.html", db_ok=db_ok, db_err=db_err)


# ── Customers ─────────────────────────────────────────────────────────────────

@app.route("/customers")
@login_required
def customers():
    page   = max(1, request.args.get("page", 1, type=int))
    search = request.args.get("q", "").strip()
    db_key = session.get("active_db", "staging")
    try:
        data  = proxy_call("get_customers", db=db_key, page=page, search=search)
        pages = max(1, math.ceil(data["total"] / data["limit"]))
        return render_template("customers.html",
                               customers=data["customers"],
                               total=data["total"],
                               page=page,
                               pages=pages,
                               search=search,
                               error=None)
    except Exception as e:
        return render_template("customers.html",
                               customers=[], total=0, page=1, pages=1,
                               search=search, error=str(e))


@app.route("/customer/<int:user_id>")
@login_required
def customer_profile(user_id):
    db_key = session.get("active_db", "staging")
    try:
        data = proxy_call("get_customer", db=db_key, user_id=user_id)
        for b in data["billing"]:
            try:
                b["amount_dollars"] = "{:.2f}".format(int(b.get("amount_cents") or 0) / 100)
            except Exception:
                b["amount_dollars"] = "0.00"
        now = datetime.utcnow()
        for p in data["pairings"]:
            try:
                ls = datetime.strptime(p["last_seen_at"], "%Y-%m-%d %H:%M:%S")
                p["is_online"] = (now - ls).total_seconds() < 300
            except Exception:
                p["is_online"] = False
        return render_template("customer.html",
                               account=data["account"],
                               pairings=data["pairings"],
                               billing=data["billing"],
                               fmp_history=data["fmp_history"],
                               error=None)
    except Exception as e:
        return render_template("customer.html",
                               account={}, pairings=[], billing=[], fmp_history=[],
                               error=str(e))


# ── Pi Diagnostics ────────────────────────────────────────────────────────────

@app.route("/customer/<int:user_id>/diagnostics")
@login_required
def customer_diagnostics(user_id):
    db_key = session.get("active_db", "staging")
    try:
        profile = proxy_call("get_customer", db=db_key, user_id=user_id)
        diag    = proxy_call("get_diagnostics", db=db_key, user_id=user_id)
        now = datetime.utcnow()
        for p in profile["pairings"]:
            try:
                ls = datetime.strptime(p["last_seen_at"], "%Y-%m-%d %H:%M:%S")
                p["is_online"] = (now - ls).total_seconds() < 300
            except Exception:
                p["is_online"] = False
        return render_template("diagnostics.html",
                               account=profile["account"],
                               pairings=profile["pairings"],
                               alerts=diag.get("alerts", []),
                               commands=diag.get("commands", []),
                               error=None)
    except Exception as e:
        return render_template("diagnostics.html",
                               account={"ID": user_id, "display_name": f"User {user_id}"},
                               pairings=[], alerts=[], commands=[],
                               error=str(e))


@app.route("/diagnostics")
@login_required
def diagnostics():
    return render_template("placeholder.html", section="Pi Diagnostics — open a customer profile to view diagnostics")


# ── Email Inbox ───────────────────────────────────────────────────────────────

def _email_cfg():
    e = config["email"]
    return (
        e.get("imap_host") or e.get("host"),
        e.get("address") or e.get("user"),
        e["password"],
    )


@app.route("/inbox")
@login_required
def inbox():
    filter_by = request.args.get("filter", "all")
    host, user, pw = _email_cfg()
    messages, err = fetch_inbox(host, user, pw, limit=50)

    if messages:
        # Auto-link by email address
        db_key = session.get("active_db", "staging")
        message_ids = [m["message_id"] for m in messages if m.get("message_id")]
        statuses = local_db.bulk_status(message_ids)

        for m in messages:
            m["handled"] = bool(statuses.get(m.get("message_id"), 0))
            # Check local link first
            linked_uid = local_db.get_link(m.get("message_id", ""))
            if not linked_uid and m.get("from_email"):
                try:
                    result = proxy_call("find_user_by_email", db=db_key, email=m["from_email"])
                    if result.get("user"):
                        linked_uid = result["user"]["ID"]
                        local_db.set_link(m["message_id"], linked_uid)
                except Exception:
                    pass
            m["linked_user"] = None
            if linked_uid:
                try:
                    profile = proxy_call("get_customer", db=db_key, user_id=linked_uid)
                    m["linked_user"] = profile.get("account")
                except Exception:
                    pass

        if filter_by == "handled":
            messages = [m for m in messages if m["handled"]]
        elif filter_by == "unhandled":
            messages = [m for m in messages if not m["handled"]]

    return render_template("inbox.html", messages=messages or [], error=err, filter=filter_by)


@app.route("/inbox/<uid>")
@login_required
def inbox_thread(uid):
    host, user, pw = _email_cfg()
    message, err = fetch_message(host, user, pw, uid)
    if not message:
        return render_template("inbox_thread.html", message={}, linked_user=None,
                               status={"handled": 0}, error=err or "Message not found",
                               reply_sent=False, reply_error=None, ai_draft=None)

    db_key = session.get("active_db", "staging")
    linked_user = None
    linked_uid = local_db.get_link(message.get("message_id", ""))
    if not linked_uid and message.get("from_email"):
        try:
            result = proxy_call("find_user_by_email", db=db_key, email=message["from_email"])
            if result.get("user"):
                linked_uid = result["user"]["ID"]
                local_db.set_link(message["message_id"], linked_uid)
        except Exception:
            pass
    if linked_uid:
        try:
            profile = proxy_call("get_customer", db=db_key, user_id=linked_uid)
            linked_user = profile.get("account")
        except Exception:
            pass

    status = local_db.get_status(message.get("message_id", ""))
    return render_template("inbox_thread.html",
                           message=message,
                           linked_user=linked_user,
                           status=status,
                           error=None,
                           reply_sent=request.args.get("sent"),
                           reply_error=None,
                           ai_draft=None)


@app.route("/inbox/<uid>/reply", methods=["POST"])
@login_required
def inbox_reply(uid):
    host, user, pw = _email_cfg()
    message, _ = fetch_message(host, user, pw, uid)
    body = request.form.get("reply_body", "").strip()
    if not body:
        return redirect(url_for("inbox_thread", uid=uid))
    ok, err = send_reply(host, user, pw,
                         to_addr=message["from_email"],
                         subject=message["subject"],
                         body=body)
    invalidate_cache(user)
    if ok:
        return redirect(url_for("inbox_thread", uid=uid, sent=1))
    return render_template("inbox_thread.html", message=message, linked_user=None,
                           status=local_db.get_status(message.get("message_id", "")),
                           error=None, reply_sent=False, reply_error=err, ai_draft=body)


@app.route("/inbox/<uid>/handled", methods=["POST"])
@login_required
def inbox_toggle_handled(uid):
    host, user, pw = _email_cfg()
    message, _ = fetch_message(host, user, pw, uid)
    if message and message.get("message_id"):
        local_db.toggle_handled(message["message_id"])
    return redirect(url_for("inbox_thread", uid=uid))


@app.route("/inbox/<uid>/link", methods=["POST"])
@login_required
def inbox_link(uid):
    host, user, pw = _email_cfg()
    message, _ = fetch_message(host, user, pw, uid)
    user_id = request.form.get("user_id", "").strip()
    if message and message.get("message_id") and user_id.isdigit():
        local_db.set_link(message["message_id"], int(user_id))
    return redirect(url_for("inbox_thread", uid=uid))


@app.route("/inbox/<uid>/ai-draft", methods=["POST"])
@login_required
def inbox_ai_draft(uid):
    host, user, pw = _email_cfg()
    message, err = fetch_message(host, user, pw, uid)
    if not message:
        return jsonify({"draft": None, "error": err or "Message not found"})

    db_key = session.get("active_db", "staging")
    customer_ctx = {}
    linked_uid = local_db.get_link(message.get("message_id", ""))
    if linked_uid:
        try:
            profile = proxy_call("get_customer", db=db_key, user_id=linked_uid)
            customer_ctx = profile.get("account") or {}
            customer_ctx["pairings"] = profile.get("pairings", [])
        except Exception:
            pass

    draft, err = draft_reply(config["gemini_api_key"], customer_ctx, message.get("body", ""))
    if draft:
        return jsonify({"draft": draft})
    return jsonify({"draft": None, "error": err})


# ── Tier Management ───────────────────────────────────────────────────────────

@app.route("/tiers", methods=["GET", "POST"])
@login_required
def tiers():
    db_key = session.get("active_db", "staging")
    success = error = None
    confirm = None
    form = {}

    if request.method == "POST":
        user_id  = request.form.get("user_id", "").strip()
        new_tier = request.form.get("new_tier", "").strip()
        reason   = request.form.get("reason", "").strip()
        confirmed = request.form.get("confirmed", "")
        form = {"user_id": user_id, "new_tier": new_tier, "reason": reason}

        if not user_id.isdigit() or not new_tier.isdigit() or len(reason) < 10:
            error = "User ID, tier (0–3), and reason (min 10 chars) are all required."
        elif confirmed == "1":
            try:
                result = proxy_call("update_tier", db=db_key,
                                    user_id=int(user_id), new_tier=int(new_tier), reason=reason)
                success = f"Tier updated from {result['old_tier']} → T{result['new_tier']} for user {user_id}."
                form = {}
            except Exception as e:
                error = str(e)
        else:
            try:
                profile = proxy_call("get_customer", db=db_key, user_id=int(user_id))
                old_tier = (profile.get("account") or {}).get("tier", "T0")
                confirm = {"user_id": user_id, "old_tier": old_tier,
                           "new_tier": new_tier, "reason": reason}
            except Exception as e:
                error = str(e)

    return render_template("tiers.html", success=success, error=error, confirm=confirm, form=form)


# ── Audit Log ─────────────────────────────────────────────────────────────────

@app.route("/audit")
@login_required
def audit():
    db_key = session.get("active_db", "staging")
    page   = max(1, request.args.get("page", 1, type=int))
    try:
        data  = proxy_call("get_audit_log", db=db_key, page=page)
        pages = max(1, math.ceil(data["total"] / 50))
        return render_template("audit.html", log=data["log"], total=data["total"],
                               page=page, pages=pages, error=None)
    except Exception as e:
        return render_template("audit.html", log=[], total=0, page=1, pages=1, error=str(e))


# ── FMP Reset (from customer profile) ────────────────────────────────────────

@app.route("/customer/<int:user_id>/reset-fmp", methods=["POST"])
@login_required
def reset_fmp(user_id):
    db_key = session.get("active_db", "staging")
    reason = request.form.get("reason", "").strip()
    if len(reason) < 10:
        return redirect(url_for("customer_profile", user_id=user_id))
    try:
        proxy_call("reset_fmp", db=db_key, user_id=user_id, reason=reason)
    except Exception:
        pass
    return redirect(url_for("customer_profile", user_id=user_id))


# ── Database Explorer ─────────────────────────────────────────────────────────

@app.route("/db-explorer")
@login_required
def db_explorer():
    db_key = session.get("active_db", "staging")
    selected_table = request.args.get("table", "")
    search = request.args.get("q", "").strip()
    page   = max(1, request.args.get("page", 1, type=int))

    if selected_table and selected_table not in ALLOWED_TABLES:
        selected_table = ""

    rows = columns = None
    total = pages = 0

    if selected_table:
        try:
            data = proxy_call("browse_table", db=db_key, table=selected_table,
                              search=search, page=page)
            rows    = data.get("rows", [])
            columns = data.get("columns", [])
            total   = data.get("total", 0)
            pages   = max(1, math.ceil(total / 50))
        except Exception as e:
            return render_template("db_explorer.html", tables=ALLOWED_TABLES,
                                   selected_table=selected_table, search=search,
                                   page=1, pages=1, total=0,
                                   rows=[], columns=[], db_key=db_key,
                                   error=str(e))

    return render_template("db_explorer.html",
                           tables=ALLOWED_TABLES,
                           selected_table=selected_table,
                           search=search,
                           page=page,
                           pages=pages,
                           total=total,
                           rows=rows,
                           columns=columns or [],
                           db_key=db_key,
                           error=None)


@app.route("/db-explorer/export")
@login_required
def db_explorer_export():
    db_key = session.get("active_db", "staging")
    table  = request.args.get("table", "")
    search = request.args.get("q", "").strip()

    if not table or table not in ALLOWED_TABLES:
        return "Invalid table", 400

    try:
        data = proxy_call("browse_table", db=db_key, table=table,
                          search=search, page=1, limit=10000)
        rows    = data.get("rows", [])
        columns = data.get("columns", [])

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        buf.seek(0)
        return Response(
            buf.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={table}.csv"}
        )
    except Exception as e:
        return str(e), 500


# ── Fleets ────────────────────────────────────────────────────────────────────

@app.route("/fleets")
@login_required
def fleets():
    page   = max(1, request.args.get("page", 1, type=int))
    db_key = session.get("active_db", "staging")
    try:
        data  = proxy_call("get_fleets", db=db_key, page=page)
        pages = max(1, math.ceil(data["total"] / data.get("limit", 20)))
        return render_template("fleet.html",
                               fleets=data["fleets"],
                               total=data["total"],
                               page=page,
                               pages=pages,
                               fleet=None,
                               error=None)
    except Exception as e:
        return render_template("fleet.html",
                               fleets=[], total=0, page=1, pages=1,
                               fleet=None, error=str(e))


@app.route("/fleet/<int:fleet_id>")
@login_required
def fleet_detail(fleet_id):
    db_key = session.get("active_db", "staging")
    try:
        data = proxy_call("get_fleet_detail", db=db_key, fleet_id=fleet_id)
        return render_template("fleet.html",
                               fleets=None,
                               fleet=data,
                               total=0, page=1, pages=1,
                               error=None)
    except Exception as e:
        return render_template("fleet.html",
                               fleets=None,
                               fleet={"fleet_id": fleet_id},
                               total=0, page=1, pages=1,
                               error=str(e))


@app.route("/fleet/<int:fleet_id>/suspend", methods=["POST"])
@login_required
def fleet_suspend(fleet_id):
    db_key = session.get("active_db", "staging")
    reason = request.form.get("reason", "").strip()
    if len(reason) < 5:
        return redirect(url_for("fleet_detail", fleet_id=fleet_id))
    try:
        proxy_call("suspend_fleet", db=db_key, fleet_id=fleet_id, reason=reason)
    except Exception:
        pass
    return redirect(url_for("fleet_detail", fleet_id=fleet_id))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
