#!/usr/bin/env bash
# verify-bug36.sh — Tier-1 §25.8 verification of a Tier-3 BUG-36 submission.
# Objective pass/fail. Run from the Helm-OS repo root. Read-only.
set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2

F=deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js
fail=0
chk(){ if [ "$2" = "PASS" ]; then printf '  \033[32mPASS\033[0m  %s\n' "$1"; else printf '  \033[31mFAIL\033[0m  %s — %s\n' "$1" "$3"; fail=1; fi; }

echo "── BUG-36 Tier-1 verification ─────────────────────────────"

# 1. diff shape: exactly 6 insertions, 0 deletions in instruments.js
stat_line=$(git diff --numstat -- "$F" | head -1)
ins=$(echo "$stat_line" | cut -f1); del=$(echo "$stat_line" | cut -f2)
ins=${ins:-0}; del=${del:-0}
[ "$ins" = "6" ] && chk "diff = 6 insertions" PASS || chk "diff = 6 insertions" FAIL "got $ins"
[ "$del" = "0" ] && chk "diff = 0 deletions"  PASS || chk "diff = 0 deletions"  FAIL "got $del — handler bodies may have been replaced"

# 2. no other file in the canonical tree was touched
others=$(git diff --name-only -- deployment/v0.9.9.4 | grep -v "instruments.js" | grep -v "tools/verify-bug36.sh" | wc -l)
[ "$others" = "0" ] && chk "no other canonical file changed" PASS || chk "no other canonical file changed" FAIL "$others extra"

# 3. superseded trees untouched
sup=$(git diff --name-only -- deployment/v0.9.4/pi_source deployment/d3kOS | wc -l)
[ "$sup" = "0" ] && chk "superseded trees untouched" PASS || chk "superseded trees untouched" FAIL "$sup changed"

# 4. S105 regression guards
[ "$(grep -c '_lastSogKts' "$F")" = "3" ] && chk "S105 _lastSogKts intact (3 sites)" PASS \
  || chk "S105 _lastSogKts intact (3 sites)" FAIL "got $(grep -c '_lastSogKts' "$F")"
grep -q 'window.SK_HANDLERS' "$F" && chk "test seam intact" PASS || chk "test seam intact" FAIL "missing"

# 5. Signal K paths unchanged (BUG-29 must NOT be pre-empted here)
[ "$(grep -c 'propulsion\.0\.' "$F")" = "8" ] && chk "propulsion.0.* unchanged (8)" PASS \
  || chk "propulsion.0.* unchanged (8)" FAIL "got $(grep -c 'propulsion\.0\.' "$F") — BUG-29 must not be done here"

# 6. behavioural check incl. the fuel fraction trap
node -e '
const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs");
const vc=new VirtualConsole(); vc.on("jsdomError",()=>{});
const d=new JSDOM("<!doctype html><html><body></body></html>",{runScripts:"outside-only",virtualConsole:vc});
d.window.eval(fs.readFileSync(process.argv[1],"utf8"));
const w=d.window;
if(!w._d3kEngData){console.log("NOCACHE");process.exit(0);}
const init=JSON.stringify(w._d3kEngData);
w.SK_HANDLERS["propulsion.0.coolantTemperature"](368.15);
w.SK_HANDLERS["propulsion.0.oilPressure"](344738);
w.SK_HANDLERS["propulsion.0.revolutions"](30);
w.SK_HANDLERS["tanks.fuel.0.currentLevel"](0.5);
w.SK_HANDLERS["electrical.batteries.0.voltage"](12.64);
const e=w._d3kEngData;
console.log(JSON.stringify({init,coolant:Math.round(e.coolant_c),oil:e.oil_psi,rpm:e.rpm,fuel:e.fuel_pct,bat:e.bat_v}));
' "$F" > /tmp/b36.json 2>/dev/null
out=$(cat /tmp/b36.json 2>/dev/null)
if [ "$out" = "NOCACHE" ] || [ -z "$out" ]; then
  chk "cache populates from handlers" FAIL "window._d3kEngData absent — not implemented yet"
else
  echo "$out" | grep -q '"coolant":95'  && chk "coolant_c = 95"        PASS || chk "coolant_c = 95" FAIL "$out"
  echo "$out" | grep -q '"oil":50'      && chk "oil_psi = 50"          PASS || chk "oil_psi = 50" FAIL "$out"
  echo "$out" | grep -q '"rpm":1800'    && chk "rpm = 1800"            PASS || chk "rpm = 1800" FAIL "$out"
  echo "$out" | grep -q '"bat":12.6'    && chk "bat_v = 12.6"          PASS || chk "bat_v = 12.6" FAIL "$out"
  echo "$out" | grep -q '"fuel":0.5'    && chk "fuel_pct = FRACTION"   PASS || chk "fuel_pct = FRACTION" FAIL "100x error — stored a percentage: $out"
  echo "$out" | grep -q '"init":"{\\"coolant_c\\":null' && chk "cache initialises all-null" PASS || chk "cache initialises all-null" FAIL "$out"
fi

echo "───────────────────────────────────────────────────────────"
[ $fail -eq 0 ] && { echo "RESULT: ACCEPT"; exit 0; } || { echo "RESULT: REJECT — return to Tier 3"; exit 1; }
