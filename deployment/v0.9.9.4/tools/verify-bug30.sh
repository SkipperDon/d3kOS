#!/usr/bin/env bash
# verify-bug30.sh — Tier-1 §25.8 verification of a Tier-3 BUG-30 submission. Read-only.
set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
F=deployment/v0.9.9.4/opt/d3kos/services/dashboard/static/js/instruments.js
fail=0
chk(){ if [ "$2" = PASS ]; then printf '  \033[32mPASS\033[0m  %s\n' "$1"; else printf '  \033[31mFAIL\033[0m  %s — %s\n' "$1" "$3"; fail=1; fi; }
echo "── BUG-30 Tier-1 verification ─────────────────────────────"
o=$(git diff --numstat -- "$F"); ins=$(echo "$o"|cut -f1); del=$(echo "$o"|cut -f2)
[ "${del:-0}" = 6 ] && chk "6 deletions (the old inline handler only)" PASS || chk "6 deletions" FAIL "got ${del:-0}"
others=$(git diff --name-only -- deployment/v0.9.9.4 | grep -v "instruments.js" | grep -v "tools/verify-bug30.sh" | wc -l)
[ "$others" = 0 ] && chk "no other canonical file changed" PASS || chk "no other canonical file changed" FAIL "$others"
grep -q "depth:   { adv: 3,    alrt: 2,    crit: 1    }" "$F" && chk "THR.depth unchanged" PASS || chk "THR.depth unchanged" FAIL "thresholds altered"
grep -qE "offset|transducerToKeel|belowSurface" "$F" && chk "no client-side offset arithmetic" FAIL "offset logic present" || chk "no client-side offset arithmetic" PASS

node -e '
const {JSDOM,VirtualConsole}=require("jsdom"),fs=require("fs");
const F=process.argv[1];
function load(){const vc=new VirtualConsole();vc.on("jsdomError",()=>{});
 const d=new JSDOM(`<!doctype html><html><body><div id="cellDepth"><div class="ic-v"></div><div class="ic-u"></div></div>`+
 `<div id="rowEngine" class="hidden"></div><div id="rowNav" class="hidden"></div>`+
 `<div id="engineAlert"></div><div id="navAlert"></div><div id="ticker"></div></body></html>`,
 {runScripts:"outside-only",virtualConsole:vc});
 d.window.openDiag=()=>{}; d.window.eval(fs.readFileSync(F,"utf8")); return d.window;}
const V=w=>w.document.querySelector("#cellDepth .ic-v").innerHTML;
const U=w=>w.document.querySelector("#cellDepth .ic-u").textContent;
const r={};
let w=load(); r.hasHandler=!!w.SK_HANDLERS["environment.depth.belowTransducer"];
w=load(); w.SK_HANDLERS["environment.depth.belowTransducer"](4.2); r.t_val=V(w); r.t_unit=U(w);
w=load(); w.SK_HANDLERS["environment.depth.belowKeel"](3.5); r.k_val=V(w); r.k_unit=U(w);
// SAFETY 1: transducer must not overwrite keel
w=load(); w.SK_HANDLERS["environment.depth.belowKeel"](3.5); w.SK_HANDLERS["environment.depth.belowTransducer"](4.2);
r.s1_val=V(w); r.s1_unit=U(w);
// keel arriving later takes over
w=load(); w.SK_HANDLERS["environment.depth.belowTransducer"](4.2); w.SK_HANDLERS["environment.depth.belowKeel"](3.5);
r.s2_val=V(w); r.s2_unit=U(w);
// alarms on both sources
w=load(); w.SK_HANDLERS["environment.depth.belowKeel"](0.5); r.a_keel=U(w);
w=load(); w.SK_HANDLERS["environment.depth.belowTransducer"](0.5); r.a_tran=U(w);
// regressions
w=load(); r.cache=!!w._d3kEngData; r.cog=/_lastSogKts/.test(fs.readFileSync(F,"utf8"));
console.log(JSON.stringify(r));
' "$F" > /tmp/b30.json 2>/dev/null
j(){ python3 -c "import json;print(json.load(open('/tmp/b30.json'))['$1'])"; }

[ "$(j hasHandler)" = True ] && chk "belowTransducer handler registered" PASS || chk "belowTransducer handler registered" FAIL "absent"
[ "$(j t_val)" = 4.2 ] && chk "transducer value renders" PASS || chk "transducer value renders" FAIL "$(j t_val)"
case "$(j t_unit)" in *"UNDER TRANSDUCER"*) chk "SAFETY: transducer reading is labelled UNDER TRANSDUCER" PASS;; *) chk "SAFETY: transducer label" FAIL "'$(j t_unit)'";; esac
[ "$(j k_val)" = 3.5 ] && chk "keel value renders" PASS || chk "keel value renders" FAIL "$(j k_val)"
case "$(j k_unit)" in *TRANSDUCER*) chk "keel label is clean" FAIL "'$(j k_unit)'";; *) chk "keel label is clean (plain metres)" PASS;; esac
[ "$(j s1_val)" = 3.5 ] && chk "SAFETY: transducer does NOT overwrite keel" PASS || chk "SAFETY: transducer overwrote keel" FAIL "showed $(j s1_val) — overstates clearance"
case "$(j s1_unit)" in *TRANSDUCER*) chk "SAFETY: label stayed on keel" FAIL "'$(j s1_unit)'";; *) chk "SAFETY: label stayed on keel" PASS;; esac
[ "$(j s2_val)" = 3.5 ] && chk "keel takes over when it arrives later" PASS || chk "keel takes over" FAIL "$(j s2_val)"
case "$(j a_keel)" in *crit*|*alrt*|*adv*) chk "shallow alarm renders (keel)" PASS;; *) chk "shallow alarm (keel)" FAIL "'$(j a_keel)'";; esac
case "$(j a_tran)" in *crit*|*alrt*|*adv*) chk "shallow alarm renders (transducer)" PASS;; *) chk "shallow alarm (transducer)" FAIL "'$(j a_tran)'";; esac
[ "$(j cache)" = True ] && chk "REGRESSION: BUG-36 cache intact" PASS || chk "REGRESSION: BUG-36 cache" FAIL "gone"
[ "$(j cog)" = True ]   && chk "REGRESSION: S105 COG gate intact" PASS || chk "REGRESSION: S105 COG gate" FAIL "gone"
echo "───────────────────────────────────────────────────────────"
[ $fail -eq 0 ] && { echo "RESULT: ACCEPT"; exit 0; } || { echo "RESULT: REJECT"; exit 1; }
