#!/usr/bin/env bash
# verify-bug37.sh — Tier-1 §25.8 verification of a Tier-3 BUG-37 submission. Read-only.
set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
A=deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py
fail=0
chk(){ if [ "$2" = PASS ]; then printf '  \033[32mPASS\033[0m  %s\n' "$1"; else printf '  \033[31mFAIL\033[0m  %s — %s\n' "$1" "$3"; fail=1; fi; }
echo "── BUG-37 Tier-1 verification ─────────────────────────────"

del=$(git diff --numstat -- $A | cut -f2); del=${del:-0}
[ "$del" = 0 ] && chk "0 deletions (additions only)" PASS || chk "0 deletions (additions only)" FAIL "$del"
others=$(git diff --name-only -- deployment/v0.9.9.4 | grep -v "dashboard/app.py" | grep -v "tools/verify-bug37.sh" | wc -l)
[ "$others" = 0 ] && chk "no other canonical file changed" PASS || chk "no other canonical file changed" FAIL "$others"
ac=$(git diff --name-only -- deployment/v0.9.9.4/opt/d3kos/services/dashboard/templates/anchor-watch.html | wc -l)
[ "$ac" = 0 ] && chk "anchor-watch.html untouched" PASS || chk "anchor-watch.html untouched" FAIL "modified"
sup=$(git diff --name-only -- deployment/v0.9.4/pi_source deployment/d3kOS | wc -l)
[ "$sup" = 0 ] && chk "superseded trees untouched" PASS || chk "superseded trees untouched" FAIL "$sup"

python3 -m py_compile $A 2>/dev/null && chk "py_compile clean" PASS || chk "py_compile clean" FAIL "syntax error"

python3 - <<'PY' > /tmp/b37.txt 2>&1
import ast, pathlib, collections
A = pathlib.Path('deployment/v0.9.9.4/opt/d3kos/services/dashboard/app.py')
tree = ast.parse(A.read_text())
routes = collections.defaultdict(set); fnames = []
for n in ast.walk(tree):
    if isinstance(n, ast.FunctionDef):
        fnames.append(n.name)
        for d in n.decorator_list:
            if isinstance(d, ast.Call) and getattr(d.func,'attr','')=='route':
                m={'GET'}
                for kw in d.keywords:
                    if kw.arg=='methods': m={e.value for e in kw.value.elts}
                routes[d.args[0].value] |= m
dups=[k for k,v in collections.Counter(fnames).items() if v>1]
exp={'/config/tier':{'GET'},'/anchor/set':{'POST'},'/anchor/state':{'GET'},
     '/anchor/clear':{'POST'},'/anchor/dismiss':{'POST'},'/anchor/advice':{'GET'},
     '/helm/mute':{'POST'}}
print("DUPS:", ",".join(dups) if dups else "none")
print("MISSING:", ",".join(r for r in exp if r not in routes) or "none")
print("BADMETH:", ",".join(f"{r}{exp[r]-routes.get(r,set())}" for r in exp if not exp[r] <= routes.get(r,set())) or "none")
print("GUARDS:", ",".join(r for r in ('/','/settings','/anchor-watch','/engine-monitor','/manual') if r not in routes) or "all-present")
print("TOTALROUTES:", len(routes))
PY
g(){ grep "^$1:" /tmp/b37.txt | cut -d' ' -f2-; }
[ "$(g DUPS)" = none ]            && chk "no duplicate view-function names" PASS || chk "no duplicate view-function names" FAIL "$(g DUPS)"
[ "$(g MISSING)" = none ]         && chk "all 7 routes registered"          PASS || chk "all 7 routes registered"          FAIL "$(g MISSING)"
[ "$(g BADMETH)" = none ]         && chk "all 7 have correct methods"       PASS || chk "all 7 have correct methods"       FAIL "$(g BADMETH)"
[ "$(g GUARDS)" = all-present ]   && chk "5 pre-existing routes survive"    PASS || chk "5 pre-existing routes survive"    FAIL "$(g GUARDS)"

echo "───────────────────────────────────────────────────────────"
[ $fail -eq 0 ] && { echo "RESULT: ACCEPT"; exit 0; } || { echo "RESULT: REJECT"; exit 1; }
