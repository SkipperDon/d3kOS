#!/usr/bin/env bash
# verify-bug35.sh — Tier-1 §25.8 verification of a Tier-3 BUG-35 submission. Read-only.
set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 2
C=deployment/v0.9.9.4/opt/d3kos/services/cloud-agent/ota_upgrade.py
S=deployment/v0.9.9.4/opt/d3kos/services/ota_upgrade.py
fail=0
chk(){ if [ "$2" = PASS ]; then printf '  \033[32mPASS\033[0m  %s\n' "$1"; else printf '  \033[31mFAIL\033[0m  %s — %s\n' "$1" "$3"; fail=1; fi; }
echo "── BUG-35 Tier-1 verification ─────────────────────────────"
diff -q "$C" "$S" >/dev/null && chk "the two copies still differ" FAIL "identical — step 7b destroyed" || chk "the two copies still differ" PASS
git show HEAD:$C | sed -n '/# 7b. Update version field in license.json/,/^$/p' > /tmp/7b.o
sed -n '/# 7b. Update version field in license.json/,/^$/p' "$C" > /tmp/7b.n
diff -q /tmp/7b.o /tmp/7b.n >/dev/null && chk "step 7b byte-identical" PASS || chk "step 7b byte-identical" FAIL "changed"
git diff -- "$C" "$S" | grep -qE '^\+.*(datetime\.now|strftime|date\.today|utcnow)' \
  && chk "no invented date" FAIL "date fabricated" || chk "no invented date" PASS
for f in "$C" "$S"; do
  n=$(basename "$(dirname "$f")")
  grep -q "VERSION_FILE.write_text(f'd3kOS Version" "$f" && chk "$n: old one-liner gone" FAIL "still present" || chk "$n: old one-liner gone" PASS
  grep -q "write_version_file(latest_ver, release)" "$f" && chk "$n: step 7 calls helper" PASS || chk "$n: step 7 calls helper" FAIL "not wired"
  grep -A3 '# 7. Update version.txt' "$f" | grep -q 'except Exception as e' && chk "$n: outer try/except intact" PASS || chk "$n: outer try/except intact" FAIL "guard removed"
  python3 -m py_compile "$f" 2>/dev/null && chk "$n: py_compile clean" PASS || chk "$n: py_compile clean" FAIL "syntax"
done
python3 - <<'PY' > /tmp/b35.txt 2>&1
import importlib.util, pathlib, tempfile
FOUR=("d3kOS Version 0.9.9.4\nRelease Date: unreleased (in development)\n"
      "Status: In Development\nBuild: v0.9.9.4-dev\n")
ok=True
for n,p in [("cloud-agent","deployment/v0.9.9.4/opt/d3kos/services/cloud-agent/ota_upgrade.py"),
            ("services","deployment/v0.9.9.4/opt/d3kos/services/ota_upgrade.py")]:
    s=importlib.util.spec_from_file_location("m_"+n.replace('-','_'),p)
    m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
    d=tempfile.mkdtemp(); vf=pathlib.Path(d)/"v.txt"; vf.write_text(FOUR); m.VERSION_FILE=vf
    m.write_version_file("0.9.9.5")
    L=vf.read_text().strip().split("\n")
    ok &= (len(L)==4 and len([l for l in L if "Version" in l])==1
           and "unreleased (in development)" in L[1] and L[2]=="Status: In Development"
           and L[3]=="Build: v0.9.9.5")
print("ROUNDTRIP:", "ok" if ok else "bad")
PY
grep -q "ROUNDTRIP: ok" /tmp/b35.txt && chk "round-trip: 4 fields, 1 Version line, date+status preserved" PASS \
  || chk "round-trip: 4 fields, 1 Version line, date+status preserved" FAIL "$(cat /tmp/b35.txt)"
echo "───────────────────────────────────────────────────────────"
[ $fail -eq 0 ] && { echo "RESULT: ACCEPT"; exit 0; } || { echo "RESULT: REJECT"; exit 1; }
