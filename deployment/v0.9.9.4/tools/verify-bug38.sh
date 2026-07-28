#!/usr/bin/env bash
# verify-bug38.sh — Tier-1 §25.8 verification of a Tier-3 BUG-38 submission. Read-only.
set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
T=deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/index.html
fail=0
chk(){ if [ "$2" = PASS ]; then printf '  \033[32mPASS\033[0m  %s\n' "$1"; else printf '  \033[31mFAIL\033[0m  %s — %s\n' "$1" "$3"; fail=1; fi; }
echo "── BUG-38 Tier-1 verification ─────────────────────────────"

others=$(git diff --name-only -- deployment/v0.9.9.4 | grep -v "index.html" | grep -v "tools/verify-bug38.sh" | wc -l)
[ "$others" = 0 ] && chk "no other canonical file changed" PASS || chk "no other canonical file changed" FAIL "$others"
sup=$(git diff --name-only -- deployment/v0.9.4/pi_source deployment/d3kOS | wc -l)
[ "$sup" = 0 ] && chk "superseded trees untouched" PASS || chk "superseded trees untouched" FAIL "$sup"

# buttons must be byte-identical to HEAD
git show HEAD:$T | grep -F 'diag-btn64' > /tmp/btn.old
grep -F 'diag-btn64' $T > /tmp/btn.new
diff -q /tmp/btn.old /tmp/btn.new >/dev/null && chk "3 buttons byte-identical to HEAD" PASS || chk "3 buttons byte-identical to HEAD" FAIL "$(diff /tmp/btn.old /tmp/btn.new | head -2)"

node -e '
const {JSDOM}=require("jsdom"),fs=require("fs");
const d=new JSDOM(fs.readFileSync(process.argv[1],"utf8")).window.document;
const r={};
for(const id of ["diagTitle","diagGrid","diagAiTxt","diagBack"]) r[id]=!!d.getElementById(id);
r.clsTitle = d.getElementById("diagTitle")?.classList.contains("diag-head-title")||false;
r.clsGrid  = d.getElementById("diagGrid")?.classList.contains("diag-grid")||false;
r.clsAi    = d.getElementById("diagAiTxt")?.classList.contains("diag-ai-txt")||false;
r.cards    = d.querySelectorAll("#diagGrid .dc").length;
r.btns     = d.querySelectorAll(".diag-btn64").length;
r.aiLbl    = !!d.querySelector(".diag-ai-lbl");
r.titleTxt = (d.getElementById("diagTitle")?.textContent||"").trim();
r.aiTxt    = (d.getElementById("diagAiTxt")?.textContent||"").trim();
// fabricated numbers must not survive in the grid or the AI text (buttons are exempt)
const panel = (d.getElementById("diagGrid")?.textContent||"") + " " + r.aiTxt;
r.bogus    = ["92","52","2250","105","98","88"].filter(n=>panel.includes(n));
console.log(JSON.stringify(r));
' $T > /tmp/b38.json 2>/dev/null
o=$(cat /tmp/b38.json)
j(){ echo "$o" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }

for id in diagTitle diagGrid diagAiTxt diagBack; do
  [ "$(j $id)" = "True" ] && chk "#$id resolves" PASS || chk "#$id resolves" FAIL "absent"
done
[ "$(j clsTitle)" = True ] && chk "diagTitle keeps class diag-head-title" PASS || chk "diagTitle keeps class diag-head-title" FAIL "class lost"
[ "$(j clsGrid)"  = True ] && chk "diagGrid keeps class diag-grid"        PASS || chk "diagGrid keeps class diag-grid"        FAIL "class lost"
[ "$(j clsAi)"    = True ] && chk "diagAiTxt keeps class diag-ai-txt"     PASS || chk "diagAiTxt keeps class diag-ai-txt"     FAIL "class lost"
[ "$(j cards)"    = 0    ] && chk "#diagGrid empty (0 demo cards)"        PASS || chk "#diagGrid empty (0 demo cards)"        FAIL "$(j cards) left"
[ "$(j btns)"     = 3    ] && chk "3 .diag-btn64 buttons present"         PASS || chk "3 .diag-btn64 buttons present"         FAIL "$(j btns)"
[ "$(j aiLbl)"    = True ] && chk ".diag-ai-lbl survives"                 PASS || chk ".diag-ai-lbl survives"                 FAIL "removed"
[ "$(j titleTxt)" = "Coolant Temperature High" ] && chk "#diagTitle text preserved" PASS || chk "#diagTitle text preserved" FAIL "got '$(j titleTxt)'"
[ "$(j bogus)"    = "[]"  ] && chk "no fabricated readings in panel"      PASS || chk "no fabricated readings in panel"      FAIL "$(j bogus)"

echo "───────────────────────────────────────────────────────────"
[ $fail -eq 0 ] && { echo "RESULT: ACCEPT"; exit 0; } || { echo "RESULT: REJECT"; exit 1; }
