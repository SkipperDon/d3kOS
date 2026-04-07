"""
DB proxy client — calls admin-api.php on HostPapa instead of connecting
to MySQL directly (shared hosting blocks remote MySQL connections).
"""
import requests
from config import config

_proxy_url = config["proxy_url"]
_api_key   = config["proxy_api_key"]
_headers   = {"Authorization": f"Bearer {_api_key}", "Content-Type": "application/json"}
_timeout   = 15


def proxy_call(action: str, db: str = "staging", **kwargs) -> dict:
    """Call the PHP proxy. Returns parsed JSON dict. Raises on HTTP error."""
    payload = {"action": action, "db": db, **kwargs}
    resp = requests.post(_proxy_url, json=payload, headers=_headers, timeout=_timeout)
    resp.raise_for_status()
    return resp.json()


def test_connection(db: str = "staging") -> tuple[bool, str | None]:
    """Returns (True, None) on success or (False, error_message) on failure."""
    try:
        result = proxy_call("test_db", db=db)
        return True, result.get("server")
    except Exception as e:
        return False, str(e)
