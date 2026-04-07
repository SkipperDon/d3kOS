"""
v0.9.7 Phase 3 — ticket diagnose + resolve routes for app.py
Insert before:  if __name__ == "__main__":

Also add to imports at top of app.py:
    from ai_client import draft_reply, diagnose_pi
    import base64 as _b64

Also add near _tickets_url line:
    _diag_bundle_url = config["proxy_url"].replace("admin-api.php", "diagnostic-bundle.php")
"""

# ── /ticket/<id>/bundle-status  (AJAX — used by ticket detail page) ───────────
@app.route("/ticket/<int:ticket_id>/bundle-status")
@login_required
def ticket_bundle_status(ticket_id):
    """Return bundle metadata (no bundle data) for the ticket detail panel."""
    url = _diag_bundle_url
    headers = _tickets_headers.copy()
    headers.pop("Content-Type", None)   # GET request — no content-type
    try:
        resp = _requests.get(url, params={"ticket_id": ticket_id}, headers=headers, timeout=15)
        data = resp.json()
        if data.get("success"):
            d = data["data"]
            return jsonify({
                "has_bundle":         True,
                "bundle_id":          d["bundle_id"],
                "bundle_size_bytes":  d["bundle_size_bytes"],
                "created_at":         d["created_at"],
                "ai_diagnosis":       d.get("ai_diagnosis"),
            })
        return jsonify({"has_bundle": False})
    except Exception as e:
        return jsonify({"has_bundle": False, "error": str(e)})


# ── /ticket/<id>/diagnose  (POST — runs AI diagnosis) ─────────────────────────
@app.route("/ticket/<int:ticket_id>/diagnose", methods=["POST"])
@login_required
def ticket_diagnose(ticket_id):
    """Download bundle, run Gemini diagnosis, store result, return JSON."""
    url = _diag_bundle_url
    headers = _tickets_headers.copy()
    headers.pop("Content-Type", None)

    try:
        # 1. Fetch bundle from HostPapa
        resp = _requests.get(url, params={"ticket_id": ticket_id}, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            return jsonify({"success": False, "error": data.get("error", "Bundle fetch failed")}), 400

        bundle_b64 = data["data"]["bundle_b64"]

        # 2. Run Gemini diagnosis
        diagnosis, err = diagnose_pi(config["gemini_api_key"], bundle_b64)
        if err:
            return jsonify({"success": False, "error": f"AI error: {err}"}), 500

        # 3. Store diagnosis back in DB
        import json as _json_mod
        diagnosis_text = _json_mod.dumps(diagnosis)
        proxy_call_tickets("save_diagnosis", ticket_id=ticket_id, ai_diagnosis=diagnosis_text)

        return jsonify({"success": True, "diagnosis": diagnosis})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
