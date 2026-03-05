import { useState, useEffect, useCallback } from "react";

const AGENT_URL = "http://YOUR_VM_IP:11435/health"; // ← change this

const STATUS_CONFIG = {
  healthy:    { color: "#00ff9d", label: "HEALTHY",    pulse: true  },
  degraded:   { color: "#ffb800", label: "DEGRADED",   pulse: true  },
  hung:       { color: "#ff4444", label: "HUNG",       pulse: false },
  down:       { color: "#ff4444", label: "DOWN",       pulse: false },
  restarting: { color: "#7b8cff", label: "RESTARTING", pulse: true  },
  starting:   { color: "#7b8cff", label: "STARTING",   pulse: true  },
  unknown:    { color: "#555",    label: "UNKNOWN",    pulse: false },
};

function Pulse({ color }) {
  return (
    <span style={{ position: "relative", display: "inline-block", width: 10, height: 10 }}>
      <span style={{
        position: "absolute", inset: 0, borderRadius: "50%",
        backgroundColor: color, opacity: 0.4,
        animation: "ping 1.5s ease-in-out infinite",
      }} />
      <span style={{
        position: "absolute", inset: "2px", borderRadius: "50%",
        backgroundColor: color,
      }} />
    </span>
  );
}

function Metric({ label, value, unit = "", warn = false, critical = false }) {
  const color = critical ? "#ff4444" : warn ? "#ffb800" : "#aaa";
  return (
    <div style={{
      background: "rgba(255,255,255,0.03)",
      border: `1px solid ${critical ? "#ff444440" : warn ? "#ffb80040" : "#ffffff15"}`,
      borderRadius: 8, padding: "12px 16px",
    }}>
      <div style={{ fontSize: 10, letterSpacing: "0.12em", color: "#555", textTransform: "uppercase", marginBottom: 6 }}>
        {label}
      </div>
      <div style={{ fontSize: 24, fontFamily: "'Space Mono', monospace", color, fontWeight: 700 }}>
        {value ?? "—"}
        {unit && <span style={{ fontSize: 13, color: "#444", marginLeft: 4 }}>{unit}</span>}
      </div>
    </div>
  );
}

function Bar({ pct, warn = 85, critical = 95 }) {
  if (pct == null) return <div style={{ color: "#444", fontSize: 12 }}>No GPU detected</div>;
  const color = pct >= critical ? "#ff4444" : pct >= warn ? "#ffb800" : "#00ff9d";
  return (
    <div style={{ background: "#111", borderRadius: 4, height: 6, overflow: "hidden", marginTop: 8 }}>
      <div style={{
        width: `${Math.min(pct, 100)}%`, height: "100%",
        background: color, borderRadius: 4,
        transition: "width 0.6s ease, background 0.3s ease",
      }} />
    </div>
  );
}

function ModelPill({ name }) {
  return (
    <span style={{
      background: "rgba(123,140,255,0.12)", border: "1px solid rgba(123,140,255,0.3)",
      borderRadius: 20, padding: "3px 10px", fontSize: 11,
      color: "#7b8cff", fontFamily: "'Space Mono', monospace",
      letterSpacing: "0.05em",
    }}>
      {name}
    </span>
  );
}

function Check({ ok, label }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "7px 0",
      borderBottom: "1px solid #ffffff08" }}>
      <span style={{
        width: 18, height: 18, borderRadius: "50%", display: "flex",
        alignItems: "center", justifyContent: "center", fontSize: 11,
        background: ok ? "rgba(0,255,157,0.12)" : "rgba(255,68,68,0.12)",
        color: ok ? "#00ff9d" : "#ff4444", flexShrink: 0,
      }}>
        {ok ? "✓" : "✗"}
      </span>
      <span style={{ color: ok ? "#ccc" : "#ff7070", fontSize: 13 }}>{label}</span>
    </div>
  );
}

export default function OllamaMonitor() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [lastFetch, setLastFetch] = useState(null);
  const [fetching, setFetching] = useState(false);

  const fetchHealth = useCallback(async () => {
    setFetching(true);
    try {
      const resp = await fetch(AGENT_URL, { cache: "no-store" });
      const json = await resp.json();
      setData(json);
      setError(null);
    } catch (e) {
      setError("Cannot reach agent — VM may be down or agent not installed");
    } finally {
      setFetching(false);
      setLastFetch(new Date());
    }
  }, []);

  useEffect(() => {
    fetchHealth();
    const id = setInterval(fetchHealth, 15000);
    return () => clearInterval(id);
  }, [fetchHealth]);

  const status = data?.status ?? "unknown";
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.unknown;

  const timeAgo = lastFetch
    ? Math.round((Date.now() - lastFetch.getTime()) / 1000) + "s ago"
    : "—";

  return (
    <div style={{
      minHeight: "100vh", background: "#080808",
      fontFamily: "'Space Mono', 'Courier New', monospace",
      color: "#ccc", padding: "40px 32px",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
        @keyframes ping {
          0%, 100% { transform: scale(1); opacity: 0.4; }
          50% { transform: scale(2.2); opacity: 0; }
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: #111; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }
      `}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between",
        marginBottom: 40, flexWrap: "wrap", gap: 16 }}>
        <div>
          <div style={{ fontSize: 10, letterSpacing: "0.25em", color: "#444", marginBottom: 8 }}>
            TRUENAS VM · OLLAMA MONITOR
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 700, color: "#fff", letterSpacing: "-0.01em", lineHeight: 1 }}>
            System Status
          </h1>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {/* Main status badge */}
          <div style={{
            display: "flex", alignItems: "center", gap: 10,
            background: `${cfg.color}10`, border: `1px solid ${cfg.color}40`,
            borderRadius: 8, padding: "10px 18px",
          }}>
            {cfg.pulse ? <Pulse color={cfg.color} /> :
              <span style={{ width: 10, height: 10, borderRadius: "50%",
                background: cfg.color, display: "inline-block" }} />}
            <span style={{ color: cfg.color, fontSize: 13, fontWeight: 700, letterSpacing: "0.1em" }}>
              {cfg.label}
            </span>
          </div>

          {/* Refresh */}
          <button onClick={fetchHealth} style={{
            background: "#111", border: "1px solid #222", borderRadius: 8,
            color: "#555", padding: "10px 14px", cursor: "pointer", fontSize: 13,
            display: "flex", alignItems: "center", gap: 6,
          }}>
            <span style={fetching ? { display: "inline-block", animation: "spin 0.8s linear infinite" } : {}}>↻</span>
          </button>
        </div>
      </div>

      {error ? (
        <div style={{
          background: "rgba(255,68,68,0.08)", border: "1px solid #ff444440",
          borderRadius: 12, padding: 24, color: "#ff7070",
        }}>
          ⚠ {error}
          <div style={{ fontSize: 11, color: "#555", marginTop: 8 }}>
            Make sure ollama-agent.py is running inside the VM on port 11435.
          </div>
        </div>
      ) : (
        <>
          {/* Checks row */}
          <div style={{
            background: "#0d0d0d", border: "1px solid #1a1a1a",
            borderRadius: 12, padding: "4px 20px", marginBottom: 24,
          }}>
            <Check ok={data?.ollama_running} label="Ollama process running" />
            <Check ok={data?.api_reachable} label="API reachable on :11434" />
            <Check ok={data?.inference_ok}  label={`Inference probe${data?.active_model ? ` (${data.active_model})` : ""}`} />
          </div>

          {/* Metrics grid */}
          <div style={{
            display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
            gap: 12, marginBottom: 24,
          }}>
            <Metric label="RAM Used" value={data?.ram_used_pct} unit="%"
              warn={data?.ram_used_pct >= 85} critical={data?.ram_used_pct >= 95} />
            <Metric label="VRAM Used" value={data?.vram_used_pct} unit="%"
              warn={data?.vram_used_pct >= 85} critical={data?.vram_used_pct >= 95} />
            <Metric label="VRAM Used" value={data?.vram_used_mb != null ? Math.round(data.vram_used_mb) : null} unit="MB" />
            <Metric label="VRAM Total" value={data?.vram_total_mb != null ? Math.round(data.vram_total_mb) : null} unit="MB" />
            <Metric label="Restarts" value={data?.restart_count} />
            <Metric label="This Hour" value={data?.restarts_this_hour}
              warn={data?.restarts_this_hour >= 3} critical={data?.restarts_this_hour >= 5} />
          </div>

          {/* VRAM bar */}
          {data?.vram_used_pct != null && (
            <div style={{
              background: "#0d0d0d", border: "1px solid #1a1a1a",
              borderRadius: 12, padding: 20, marginBottom: 24,
            }}>
              <div style={{ fontSize: 10, letterSpacing: "0.12em", color: "#444",
                textTransform: "uppercase", marginBottom: 4 }}>
                {data.gpu_name ?? "GPU"} · VRAM
              </div>
              <Bar pct={data.vram_used_pct} />
              <div style={{ display: "flex", justifyContent: "space-between",
                fontSize: 11, color: "#444", marginTop: 6 }}>
                <span>{data.vram_used_mb != null ? Math.round(data.vram_used_mb) : 0} MB used</span>
                <span>{data.vram_total_mb != null ? Math.round(data.vram_total_mb) : "?"} MB total</span>
              </div>
            </div>
          )}

          {/* RAM bar */}
          <div style={{
            background: "#0d0d0d", border: "1px solid #1a1a1a",
            borderRadius: 12, padding: 20, marginBottom: 24,
          }}>
            <div style={{ fontSize: 10, letterSpacing: "0.12em", color: "#444",
              textTransform: "uppercase", marginBottom: 4 }}>
              System RAM
            </div>
            <Bar pct={data?.ram_used_pct} />
            <div style={{ fontSize: 11, color: "#444", marginTop: 6 }}>
              {data?.ram_used_pct ?? "—"}% used
            </div>
          </div>

          {/* Models */}
          {data?.models?.length > 0 && (
            <div style={{
              background: "#0d0d0d", border: "1px solid #1a1a1a",
              borderRadius: 12, padding: 20, marginBottom: 24,
            }}>
              <div style={{ fontSize: 10, letterSpacing: "0.12em", color: "#444",
                textTransform: "uppercase", marginBottom: 12 }}>
                Loaded Models ({data.models.length})
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {data.models.map(m => <ModelPill key={m} name={m} />)}
              </div>
            </div>
          )}

          {/* Errors / Warnings */}
          {[...(data?.errors ?? []), ...(data?.warnings ?? [])].length > 0 && (
            <div style={{
              background: "rgba(255,68,68,0.05)", border: "1px solid #ff444430",
              borderRadius: 12, padding: 20, marginBottom: 24,
            }}>
              <div style={{ fontSize: 10, letterSpacing: "0.12em", color: "#ff444480",
                textTransform: "uppercase", marginBottom: 12 }}>
                Active Issues
              </div>
              {data.errors?.map((e, i) => (
                <div key={i} style={{ color: "#ff7070", fontSize: 13, padding: "4px 0",
                  borderBottom: "1px solid #ffffff08", display: "flex", gap: 8 }}>
                  <span style={{ color: "#ff4444" }}>✗</span> {e}
                </div>
              ))}
              {data.warnings?.map((w, i) => (
                <div key={i} style={{ color: "#ffd070", fontSize: 13, padding: "4px 0",
                  borderBottom: "1px solid #ffffff08", display: "flex", gap: 8 }}>
                  <span style={{ color: "#ffb800" }}>⚠</span> {w}
                </div>
              ))}
            </div>
          )}

          {/* Footer */}
          <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap",
            gap: 8, fontSize: 11, color: "#333", borderTop: "1px solid #1a1a1a", paddingTop: 16 }}>
            <span>Agent started: {data?.agent_start ? new Date(data.agent_start).toLocaleString() : "—"}</span>
            <span>Last check: {data?.last_check ? new Date(data.last_check).toLocaleTimeString() : "—"} · Refreshed {timeAgo}</span>
          </div>
        </>
      )}
    </div>
  );
}
