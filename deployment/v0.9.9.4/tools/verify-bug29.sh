#!/usr/bin/env bash
# verify-bug29.sh — Tier-1 §25.8 verification of a Tier-3 BUG-29 submission. Read-only.
set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
D=deployment/v0.9.9.4/opt/d3kos/services/dashboard
fail=0
chk(){ if [ "$2" = PASS ]; then printf '  \033[32mPASS\033[0m  %s\n' "$1"; else printf '  \033[31mFAIL\033[0m  %s — %s\n' "$1" "$3"; fail=1; fi; }
echo "── BUG-29 Tier-1 verification ─────────────────────────────"
others=$(git diff --name-only -- deployment/v0.9.9.4 | grep -vE "instruments.js|boatlog-engine.js|engine-monitor.html|helm-assistant.html|tools/verify-bug29.sh" | wc -l)
[ "$others" = 0 ] && chk "only the four target files changed" PASS || chk "only the four target files changed" FAIL "$others extra"

node -e '
const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs");
const B="deployment/v0.9.9.4/opt/d3kos/services/dashboard/";
const vc=new VirtualConsole();vc.on("jsdomError",()=>{});
const d=new JSDOM(`<!doctype html><html><body><div id="rowEngine" class="hidden"></div>`+
 `<div id="rowNav" class="hidden"></div><div id="engineAlert"></div><div id="navAlert"></div>`+
 `<div id="ticker"></div></body></html>`,{runScripts:"outside-only",virtualConsole:vc});
d.window.openDiag=()=>{}; d.window.eval(fs.readFileSync(B+"static/js/instruments.js","utf8"));
const H=d.window.SK_HANDLERS, r={ident:[],missing:[]};
const A={"propulsion.0.revolutions":["propulsion.port.revolutions"],
 "propulsion.0.oilPressure":["propulsion.port.oilPressure"],
 "propulsion.0.coolantTemperature":["propulsion.port.temperature","propulsion.0.temperature"],
 "propulsion.0.trimTabPosition":["propulsion.port.drive.trimState","propulsion.0.drive.trimState"]};
for(const [o,as] of Object.entries(A)){
  if(!H[o]) r.missing.push("ORIGINAL "+o);
  for(const a of as){ if(!H[a]) r.missing.push(a); else if(H[a]!==H[o]) r.ident.push(a); }
}
r.batteryAliased = !!H["electrical.batteries.port.voltage"];
r.batteryOk = !!H["electrical.batteries.0.voltage"];
// behavioural: an aliased delta must reach the BUG-36 cache
d.window.SK_HANDLERS["propulsion.port.temperature"](368.15);
d.window.SK_HANDLERS["propulsion.port.revolutions"](30);
d.window.SK_HANDLERS["propulsion.port.oilPressure"](344738);
r.coolant=Math.round(d.window._d3kEngData.coolant_c); r.rpm=d.window._d3kEngData.rpm; r.oil=d.window._d3kEngData.oil_psi;
r.cog=/_lastSogKts/.test(fs.readFileSync(B+"static/js/instruments.js","utf8"));
r.depth=!!H["environment.depth.belowTransducer"];
console.log(JSON.stringify(r));
' > /tmp/b29.json 2>/tmp/b29.err
if [ ! -s /tmp/b29.json ]; then chk "instruments.js loads in jsdom" FAIL "$(head -3 /tmp/b29.err)"; else
j(){ python3 -c "import json;d=json.load(open('/tmp/b29.json'));print(d['$1'])"; }
[ "$(j missing)" = "[]" ] && chk "all originals + aliases registered" PASS || chk "all originals + aliases registered" FAIL "$(j missing)"
[ "$(j ident)"   = "[]" ] && chk "aliases share FUNCTION IDENTITY (not copies)" PASS || chk "aliases share FUNCTION IDENTITY" FAIL "copies: $(j ident)"
[ "$(j batteryAliased)" = False ] && chk "battery NOT aliased" PASS || chk "battery NOT aliased" FAIL "aliased"
[ "$(j batteryOk)" = True ] && chk "battery original intact" PASS || chk "battery original intact" FAIL "gone"
[ "$(j coolant)" = 95 ]  && chk "aliased coolant delta reaches the cache" PASS || chk "aliased coolant delta" FAIL "$(j coolant)"
[ "$(j rpm)" = 1800 ]    && chk "aliased rpm delta reaches the cache" PASS || chk "aliased rpm delta" FAIL "$(j rpm)"
[ "$(j oil)" = 50 ]      && chk "aliased oil delta reaches the cache" PASS || chk "aliased oil delta" FAIL "$(j oil)"
[ "$(j cog)" = True ]    && chk "REGRESSION: S105 COG gate intact" PASS || chk "REGRESSION: S105 COG gate" FAIL "gone"
[ "$(j depth)" = True ]  && chk "REGRESSION: BUG-30 depth fallback intact" PASS || chk "REGRESSION: BUG-30 fallback" FAIL "gone"
fi
# subscribe-list coverage in the three files that use one
for f in static/js/boatlog-engine.js templates/engine-monitor.html templates/helm-assistant.html; do
  n=$(basename "$f"); miss=""
  for a in propulsion.port.revolutions propulsion.port.oilPressure propulsion.port.temperature; do
    base=$(echo "$a" | sed 's/port/0/;s/\.temperature/.coolantTemperature/')
    grep -q "$base" "$D/$f" || continue
    grep -qE "path: *'${a//./\\.}'" "$D/$f" || miss="$miss $a"
  done
  [ -z "$miss" ] && chk "$n: aliases present in subscribe list" PASS || chk "$n: subscribe list" FAIL "missing:$miss"
done
echo "───────────────────────────────────────────────────────────"
[ $fail -eq 0 ] && { echo "RESULT: ACCEPT"; exit 0; } || { echo "RESULT: REJECT"; exit 1; }
