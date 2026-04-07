"""
diagnose_pi() — add this function to the existing ai_client.py on the CRM VM.
Paste below the existing draft_reply() function.
"""
import json as _json
import tarfile as _tarfile
import io as _io
import base64 as _base64

# Max chars of log text to send Gemini — keeps cost and latency down
_DIAG_MAX_CHARS = 40000

# Priority order for log extraction from bundle
_LOG_PRIORITY = [
    'services_status.txt',
    'syslog_24h.txt',
    'dmesg.txt',
    'ps_aux.txt',
    'df_h.txt',
    'free_h.txt',
    'kern_log.txt',
]

DIAG_SYSTEM_PROMPT = """You are a marine electronics diagnostic AI for AtMyBoat.com.
You analyse d3kOS Raspberry Pi system logs and identify the root cause of problems.

d3kOS is a marine navigation and monitoring system running on a Raspberry Pi.
Services include: SignalK (NMEA data), Node-RED (automation), cloud-agent (remote commands),
ai-bridge (voice AI), fleet-push (vessel tracking), predictive-maintenance, gemini-proxy.

Return your analysis as a JSON object with these exact keys:
{
  "root_cause": "one concise sentence describing the primary problem",
  "confidence": 75,
  "summary": "2-3 sentences expanding on what you found",
  "fix_steps": ["step 1", "step 2", "step 3"],
  "severity": "low|medium|high|critical"
}

Rules:
- confidence is 0-100 (be honest — low confidence if logs are inconclusive)
- fix_steps are specific actionable commands or actions, not generic advice
- If logs show no problems, say so in root_cause and set confidence=95
- Do not invent problems not evidenced in the logs
- Return ONLY the JSON object — no markdown, no explanation outside the JSON
"""


def _extract_bundle_text(bundle_b64: str) -> str:
    """Decode base64 tar.gz bundle, extract key log files, return combined text."""
    raw = _base64.b64decode(bundle_b64)
    combined = []
    total = 0

    try:
        with _tarfile.open(fileobj=_io.BytesIO(raw), mode='r:gz') as tar:
            members = {m.name.split('/')[-1]: m for m in tar.getmembers() if m.isfile()}

            for log_name in _LOG_PRIORITY:
                if total >= _DIAG_MAX_CHARS:
                    break
                member = members.get(log_name)
                if not member:
                    continue
                try:
                    f = tar.extractfile(member)
                    if f:
                        text = f.read().decode('utf-8', errors='replace')
                        remaining = _DIAG_MAX_CHARS - total
                        if len(text) > remaining:
                            text = text[:remaining] + '\n[truncated]'
                        combined.append(f'=== {log_name} ===\n{text}')
                        total += len(text)
                except Exception:
                    pass

            # Also grab d3kos_logs/*.log files
            for name, member in members.items():
                if total >= _DIAG_MAX_CHARS:
                    break
                if 'd3kos_logs' in member.name and name.endswith('.log'):
                    try:
                        f = tar.extractfile(member)
                        if f:
                            text = f.read().decode('utf-8', errors='replace')
                            remaining = _DIAG_MAX_CHARS - total
                            snippet = text[-min(3000, remaining):]  # tail of each log
                            combined.append(f'=== {name} (tail) ===\n{snippet}')
                            total += len(snippet)
                    except Exception:
                        pass
    except Exception as e:
        return f'[Bundle extraction error: {e}]'

    return '\n\n'.join(combined) if combined else '[No log content extracted]'


def diagnose_pi(api_key: str, bundle_b64: str) -> tuple:
    """
    Run AI diagnosis on a Pi diagnostic bundle.
    Returns (diagnosis_dict, error_str).
    diagnosis_dict has keys: root_cause, confidence, summary, fix_steps, severity
    """
    import requests

    log_text = _extract_bundle_text(bundle_b64)

    prompt = f"""{DIAG_SYSTEM_PROMPT}

--- SYSTEM LOGS ---
{log_text}

--- ANALYSIS ---
Return only the JSON object."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    try:
        resp = requests.post(
            url,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": 800,
                    "temperature": 0.2,
                    "responseMimeType": "application/json",
                },
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        diagnosis = _json.loads(raw)

        # Normalise — ensure all required keys present
        return {
            "root_cause": str(diagnosis.get("root_cause", "Unknown")),
            "confidence":  int(diagnosis.get("confidence", 0)),
            "summary":     str(diagnosis.get("summary", "")),
            "fix_steps":   list(diagnosis.get("fix_steps", [])),
            "severity":    str(diagnosis.get("severity", "medium")),
        }, None

    except Exception as e:
        return None, str(e)
