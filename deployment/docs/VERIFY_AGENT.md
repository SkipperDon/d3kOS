# d3kOS Verify Agent — Independent Code Verification

**Version:** 1.0 | **Date:** 2026-03-04

---

## Architecture

```
Workstation (192.168.1.36)                 TrueNAS VM (192.168.1.103)
┌─────────────────────────────┐            ┌──────────────────────────────┐
│  ollama_execute_v3.py       │            │  d3kos-verify-agent.service  │
│  └─ qwen3-coder:30b         │            │  └─ verify_agent.py          │
│     (GENERATOR role)        │──POST /verify──▶  port 11436              │
│                             │◀── {pass, score, issue, suggestion} ──────│
│  If FAIL → correction loop  │            │  Calls workstation Ollama     │
│  If PASS → apply to Pi      │            │  qwen3-coder:30b (REVIEWER)  │
└─────────────────────────────┘            └──────────────────────────────┘
```

**Two roles, same model, different prompts, different inference paths:**
- **Generator:** "Write code that implements this instruction"
- **Reviewer:** "You did NOT write this code. Verify it is correct."

This gives genuine independent review — the reviewer has no memory of generating the code and approaches it from a clean-slate critic perspective.

---

## Why TrueNAS VM runs the service (not the model)

TrueNAS runs the verify agent **service** (HTTP endpoint, logging, reporting). Inference is routed to the workstation GPU. This is intentional:

- TrueNAS bhyve VM memory bandwidth is throttled by ZFS ARC competition
- Benchmarked: 0.03 t/s for 1.5b model (unusable even for short reviews)
- Root cause: CPU sees only 2 physical cores, memory contended with NAS workloads
- TrueNAS VM is the right place for the **service layer** — always on, independent machine, logs accessible

---

## Service Details

| Property | Value |
|----------|-------|
| Service name | `d3kos-verify-agent.service` |
| Port | 11436 |
| Log | `/var/log/verify-agent.log` |
| Script | `/opt/verify-agent/verify_agent.py` |
| Inference backend | `http://192.168.1.36:11434` (workstation) |
| Model | `qwen3-coder:30b` |
| Typical response time | 5–35s (GPU-backed) |

---

## Endpoints

### `POST /verify`
Verify a generated code block.

**Request:**
```json
{
  "code":        "< generated code block >",
  "instruction": "< what the code must do (from spec section) >",
  "context":     "< surrounding file context passed to generator >",
  "filename":    "camera_stream_manager.py",
  "phase_name":  "camera-assign-validation"
}
```

**Response:**
```json
{
  "pass":       true,
  "score":      88,
  "issue":      "none",
  "suggestion": "none",
  "model":      "qwen3-coder:30b",
  "elapsed_s":  31.1
}
```

- `pass: true` → code is correct, proceed to apply
- `pass: false` → code has issues, executor triggers correction loop with `issue` + `suggestion`
- `pass: null` → verifier error (Ollama unreachable) — executor logs warning and continues

### `GET /health`
```json
{"status": "healthy", "model": "qwen3-coder:30b", "port": 11436, "stats": {...}}
```

### `GET /report`
Last 20 verify results with phase_name, filename, pass/fail, score, issue, timestamp.

### `GET /stats`
Aggregate pass/fail/error counts and pass rate %.

---

## Executor Integration (`ollama_execute_v3.py`)

The verify call is wired into both execution modes:

**Standard mode** — called on each valid block before applying:
```
Ollama generates → validate (syntax/vars) → call_verify() → apply or correct
```

**REPLACE_EXACT mode** — called after validation:
```
Ollama generates CODE → validate → call_verify() → apply or correct
```

**On FAIL:** The verify `issue` is appended to `block['issues']` and the block is marked invalid, triggering the existing correction loop. Ollama receives both the structural issues and the verify feedback in the correction prompt.

**On verifier unavailable:** `call_verify()` returns `None`, execution continues uninterrupted. The pipeline is never blocked by an offline verifier.

---

## Executor Summary Report

At the end of every run, the executor now prints:
```
Ollama generator  (qwen3-coder:30b  @ 192.168.1.36 workstation): $0.00
Ollama verifier   (qwen2.5-coder:1.5b @ 192.168.1.103 TrueNAS): $0.00
Verify stats: N calls | X pass / Y fail / Z error (nn% pass rate)
```

---

## Management

```bash
# On TrueNAS VM (ssh root@192.168.1.103)
systemctl status d3kos-verify-agent
systemctl restart d3kos-verify-agent
tail -f /var/log/verify-agent.log

# From laptop
curl http://192.168.1.103:11436/health
curl http://192.168.1.103:11436/stats
curl http://192.168.1.103:11436/report
```

---

## Configuration (`verify_agent.py`)

| Variable | Value | Notes |
|----------|-------|-------|
| `OLLAMA_URL` | `http://192.168.1.36:11434/api/generate` | Workstation GPU |
| `VERIFY_MODEL` | `qwen3-coder:30b` | Same as generator, different role |
| `VERIFY_PORT` | `11436` | TrueNAS VM listen port |
| `OLLAMA_TIMEOUT` | `120s` | GPU review completes in 30-40s |

To disable verifier globally: set `VERIFY_ENABLED = False` in `ollama_execute_v3.py`.

---

## Key Files

| File | Location |
|------|----------|
| Verify agent | `/opt/verify-agent/verify_agent.py` (TrueNAS VM) |
| Systemd service | `/etc/systemd/system/d3kos-verify-agent.service` (TrueNAS VM) |
| Executor | `/home/boatiq/Helm-OS/deployment/scripts/ollama_execute_v3.py` (laptop) |
| Source (git) | `deployment/scripts/verify_agent.py` |
| This doc | `deployment/docs/VERIFY_AGENT.md` |
