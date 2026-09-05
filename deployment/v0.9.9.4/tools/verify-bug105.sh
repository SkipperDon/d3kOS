#!/bin/bash
# verify-bug105.sh — BUG-105 / BUG-103 / BUG-102 first-boot stability (S148)
# Run ON the lab Pi as d3kos. Exit 1 on any FAIL. Textual tests T1–T7, behavioural T8–T15.
set -u
PASS=0; FAIL=0
ok()   { echo "PASS $1"; PASS=$((PASS+1)); }
bad()  { echo "FAIL $1 — $2"; FAIL=$((FAIL+1)); }
SH=/opt/d3kos/services/self-healing
UN=/etc/systemd/system
TMP=$(mktemp -d /tmp/bug105.XXXX); trap 'rm -rf "$TMP"' EXIT

# ---- textual -----------------------------------------------------------------
grep -q 'MAX_ATTEMPTS' $SH/remediation_engine.py                       && ok T1 || bad T1 "engine has no attempt cap"
grep -q "'is-active', service_name" $SH/remediation_engine.py           && ok T2 || bad T2 "engine restarts without checking state"
grep -q '_already_open' $SH/issue_detector.py                           && ok T3 || bad T3 "detector has no dedup"
grep -q "== 'failed'" $SH/issue_detector.py && ! grep -q "!= 'active'" $SH/issue_detector.py \
                                                                        && ok T4 || bad T4 "detector still flags inactive as an issue"
grep -q 'self-healing/issues.db' /opt/d3kos/scripts/sanitize.sh         && ok T5 || bad T5 "sanitize.sh does not purge issues.db"
t6=1
for u in d3kos-camera-stream d3kos-fish-detector d3kos-voice; do
  grep -q 'ExecStartPre=.*tier/feature' $UN/$u.service && t6=0
  grep -q 'ExecCondition=.*tier/feature' $UN/$u.service || t6=0
done
grep -q 'Restart=on-failure' $UN/d3kos-camera-stream.service            || t6=0
grep -q 'ConditionPathExists=/opt/d3kos/config/cloud-config.json' $UN/d3kos-live.service || t6=0
[ $t6 = 1 ] && ok T6 || bad T6 "a tier-gated unit still uses ExecStartPre / Restart=always / no live gate"
st=$(systemd-analyze cat-config systemd/journald.conf | grep -v '^#' | grep '^Storage=' | tail -1)
[ "$st" = "Storage=persistent" ]                                        && ok T7 || bad T7 "effective journald Storage is '$st'"

# ---- behavioural: engine must NOT restart a healthy service (T8) ------------------
export D3KOS_ISSUES_DB=$TMP/issues.db D3KOS_REMEDIATION_LOG=$TMP/rem.log
mk() { python3 - "$1" "$2" <<'EOF'
import sqlite3,sys,json,datetime
c=sqlite3.connect(sys.argv[1]); c.execute('''CREATE TABLE IF NOT EXISTS issues (id INTEGER PRIMARY KEY AUTOINCREMENT,
 timestamp TEXT NOT NULL, category TEXT NOT NULL, severity TEXT NOT NULL, description TEXT NOT NULL, metrics TEXT,
 status TEXT DEFAULT 'detected', resolved_at TEXT, remediation_action TEXT)''')
for s in sys.argv[2].split(','):
    c.execute("INSERT INTO issues (timestamp,category,severity,description,metrics) VALUES (?,?,?,?,?)",
      (datetime.datetime.now().isoformat(),'service_down','critical',f'Service {s} is not running',json.dumps({'service':s})))
c.commit()
EOF
}
q() { python3 -c "import sqlite3;print(sqlite3.connect('$1').execute(\"$2\").fetchone()[0])"; }
rm -f $TMP/issues.db $TMP/rem.log; mk $TMP/issues.db d3kos-dashboard
pid_before=$(systemctl show -p MainPID --value d3kos-dashboard)
sudo -E python3 $SH/remediation_engine.py --once >/dev/null 2>&1
pid_after=$(systemctl show -p MainPID --value d3kos-dashboard)
[ "$pid_before" = "$pid_after" ] && [ "$(q $TMP/issues.db "select status from issues")" = resolved ] \
  && grep -q 'no restart issued' $TMP/rem.log                          && ok T8 || bad T8 "engine restarted a HEALTHY service (pid $pid_before -> $pid_after)"

# ---- behavioural: three strikes then retire (T9), one action per service per pass (T10) ----
sudo tee /run/systemd/system/bug105-fail.service >/dev/null <<'EOF'
[Service]
Type=oneshot
ExecStart=/bin/false
EOF
sudo systemctl daemon-reload; sudo systemctl start bug105-fail.service 2>/dev/null
[ "$(systemctl is-active bug105-fail.service)" = failed ] || echo "note: bug105-fail state=$(systemctl is-active bug105-fail.service)"
rm -f $TMP/issues.db $TMP/rem.log; mk $TMP/issues.db bug105-fail,bug105-fail,bug105-fail,bug105-fail,bug105-fail
sudo -E python3 $SH/remediation_engine.py --once >/dev/null 2>&1
[ "$(grep -c 'Attempting remediation' $TMP/rem.log)" = 1 ]             && ok T10 || bad T10 "$(grep -c 'Attempting remediation' $TMP/rem.log) systemctl actions for one service in one pass"
sudo -E python3 $SH/remediation_engine.py --once >/dev/null 2>&1   # attempts are in-memory: run 3 passes in ONE process
sudo -E python3 - <<EOF   # BUG-105 harness fix (S148): the prior sudo call left rem.log root-owned;
import os,sys; sys.path.insert(0,'$SH'); os.environ['D3KOS_ISSUES_DB']='$TMP/issues.db'; os.environ['D3KOS_REMEDIATION_LOG']='$TMP/rem.log'  # stay root here so it can still append
import remediation_engine as r; e=r.RemediationEngine(); [e.run_cycle() for _ in range(3)]
EOF
[ "$(q $TMP/issues.db "select count(*) from issues where status='failed'")" = 5 ] && ok T9 || bad T9 "rows not retired after MAX_ATTEMPTS: $(q $TMP/issues.db "select status||':'||count(*) from issues group by status")"
sudo systemctl reset-failed bug105-fail.service 2>/dev/null; sudo rm -f /run/systemd/system/bug105-fail.service; sudo systemctl daemon-reload

# ---- behavioural: detector dedup (T11) ----------------------------------------------
rm -f $TMP/issues.db
python3 - <<EOF
import os,sys,json; sys.path.insert(0,'$SH'); os.environ['D3KOS_ISSUES_DB']='$TMP/issues.db'
import issue_detector as d
fake={'category':'service_down','severity':'critical','description':'Service bug105-x is not running','metrics':json.dumps({'service':'bug105-x'})}
d.detector.check_services=lambda: fake
for f in ('check_cpu_temp','check_memory','check_disk_space'): setattr(d.detector,f,lambda: None)
d.detector.detect_issues(); d.detector.detect_issues(); d.detector.detect_issues()
EOF
[ "$(q $TMP/issues.db 'select count(*) from issues')" = 1 ]            && ok T11 || bad T11 "detector inserted $(q $TMP/issues.db 'select count(*) from issues') rows for one symptom"
unset D3KOS_ISSUES_DB D3KOS_REMEDIATION_LOG

# ---- behavioural: tier-gated unit is a silent no-op at Tier 0 (T12) ----------------------
sudo systemctl reset-failed d3kos-camera-stream.service 2>/dev/null; sudo systemctl start d3kos-camera-stream.service; sleep 20
s=$(systemctl is-active d3kos-camera-stream.service)
[ "$s" = inactive ]                                                     && ok T12 || bad T12 "camera-stream is '$s' at Tier 0 (want inactive, never failed/activating)"

# ---- behavioural: re-try oneshot does not fail (T13), journald persistent+live (T14) ----------
sudo systemctl start d3kos-tier-gated.service; sleep 2
[ "$(systemctl is-failed d3kos-tier-gated.service)" = inactive ] && [ "$(systemctl is-active d3kos-tier-gated.timer)" = active ] \
                                                                        && ok T13 || bad T13 "tier-gated oneshot/timer state: $(systemctl is-failed d3kos-tier-gated.service)/$(systemctl is-active d3kos-tier-gated.timer)"
logger -t bug105 "ping-$$"; sleep 1
journalctl -t bug105 -n 3 --no-pager | grep -q "ping-$$" && journalctl --header 2>/dev/null | grep -m1 'File path' | grep -q '/var/log/journal' \
                                                                        && ok T14 || bad T14 "journald not capturing to /var/log/journal after restart"

# ---- behavioural: the storm is gone (T15) --------------------------------------------------
for u in d3kos-remediation d3kos-issue-detector; do [ "$(systemctl is-active $u)" = active ] || bad T15 "$u not active (re-enable after deploy)"; done
n=$(sudo journalctl --since '90 seconds ago' --no-pager _COMM=systemctl 2>/dev/null | grep -c 'Job for')
[ "${n:-0}" -lt 5 ]                                                      && ok T15 || bad T15 "$n failed systemctl jobs in 90 s — storm still running"

echo; echo "PASS=$PASS FAIL=$FAIL"; [ $FAIL = 0 ]
