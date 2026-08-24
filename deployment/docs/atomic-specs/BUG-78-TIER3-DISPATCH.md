# BUG-78 — TIER 3 DISPATCH

**Implementer:** Gemma-4 (`gemma4:31b-cloud`, Ollama Cloud via `192.168.1.36:11434`)
**Authorised:** operator, S131 — d3kOS source may be sent to `gemma4:31b-cloud` for Tier 3 work
**MANDATORY call option:** `"think": false` — without it Gemma-4 consumes the token budget and returns
an **empty string**, which is indistinguishable from a hang (this is what S114 mis-recorded as "never
returned in 10 minutes").
**Fallback:** `gemma4:31b-cloud` returned `"temporarily overloaded"` on the S131 probe. On that error,
retry twice, then fall back to `gemma4:latest` on the workstation for these constrained edits.

**Prerequisite:** `deployment/docs/atomic-specs/BUG-78.md` Steps 0 and 1 are COMPLETE. Do not dispatch
before both scripts are committed to the canonical tree unmodified.

**Standing rule — do not violate:** exact `old`/`new` replacements only. **Never ask Gemma-4 to generate
a whole file.** In S118 a whole-file dispatch produced invalid bash with `grep` on NUL-separated
`/proc/environ`; it was discarded and rewritten at Tier 1. The rule holds.

---

## Dispatch payload — send verbatim

```
You are editing two bash scripts. Apply EXACTLY the replacements listed below.

RULES:
1. Output ONLY the replacement blocks in the format given. No explanation, no commentary.
2. Match the `old` text EXACTLY, including indentation and blank lines.
3. Do NOT reformat, reorder, or "improve" any line you were not asked to change.
4. Do NOT output the whole file. Only the replaced regions.
5. If any `old` block does not appear verbatim in the file you were given, output
   exactly: ANCHOR MISS: <block letter>
   and stop. Do not guess a nearby match.
6. This is bash. Every variable expansion must be quoted as written.

FILE 1: sanitize.sh

--- REPLACEMENT A ---
old:
    chown d3kos:d3kos "$LICENSE_FILE"
    chmod 644 "$LICENSE_FILE"
    log "  License file reset to defaults"

new:
    chown d3kos:d3kos "$LICENSE_FILE"
    chmod 600 "$LICENSE_FILE"
    log "  License file reset to defaults (mode 600 — BUG-78 D3)"
--- END REPLACEMENT A ---

--- REPLACEMENT B ---
old:
# STEP 8: Reset license.json (clear installation ID)

new:
[see BUG-78.md section 3.2 — insert the STEP 7b block verbatim, ending with the
 original "# STEP 8: Reset license.json (clear installation ID)" line preserved]
--- END REPLACEMENT B ---

FILE 2: create-image.sh

--- REPLACEMENT C ---
[see BUG-78.md section 4.1 — the old block is the eight-line "Step 1: Pre-image
 cleanup" sequence ending in 'echo "  - Cleanup complete"']
--- END REPLACEMENT C ---
```

---

## Traps in this dispatch — Tier 1 verification must check each

These are the specific places a plausible-looking output will be wrong. **Check all six by hand.**

| # | Trap | Correct behaviour |
|---|---|---|
| 1 | `$D3K_SECRETS` is an unquoted multi-line variable in the `for` loop. This is deliberate — word-splitting is what iterates it. | Gemma-4 may "helpfully" quote it as `"$D3K_SECRETS"`, which makes the loop run **once** with a single newline-laden string and delete nothing. **Reject any output that quotes it in the `for` header.** |
| 2 | `rm -f /opt/d3kos/config/*.bak` — glob must stay unquoted. | Quoting it makes it a literal filename. Reject. |
| 3 | Replacement B must **preserve** the original `# STEP 8:` comment line at the end of the new block. | If it is dropped, the license-reset section loses its header and the next edit's anchor is destroyed. |
| 4 | `if ! "$SANITIZE" --unattended; then` — the `!` and the quoting must both survive. | A rewrite to `if [ $? -ne 0 ]` after the call is a different (and wrong) construct. |
| 5 | `$(ls -A /etc/ssh/ssh_host_*_key 2>/dev/null)` — the glob is inside the command substitution. | Gemma-4 may convert to `ls -A "/etc/ssh/ssh_host_*_key"`, which never matches. Reject. |
| 6 | `exit 1` must be present in **both** failure paths (sanitizer missing, sanitizer failed) **and** in the assertion. | A `return 1` or a bare `echo` is not a build failure. This is the entire point of the change. |

## Verification procedure (Tier 1, not Tier 3)

1. **Line-exact match, not substring.** In S114 a substring-matching checker produced a false positive
   by flagging two genuinely distinct lines that differed only in indentation (6 spaces vs 8). Compare
   whole lines.
2. `bash -n sanitize.sh && bash -n create-image.sh` — syntax check both. Non-negotiable.
3. Count the changed regions: expect exactly **3** (A, B, C). More than three means Gemma-4 edited
   something it was not asked to.
4. `git diff` must show **zero** changes outside the three regions.
5. Run `verify-bug78.sh` — 6/6 including the T6 negative test.
6. **Do not run `create-image.sh` or `sanitize.sh` on the lab Pi.** `sanitize.sh` deletes
   `~/.ssh/authorized_keys` and would sever this session's access to the Pi.

## Do not count this as a Tier 3 success unless

- `bash -n` passes on both files, **and**
- T6 (the negative assertion test) passes, **and**
- the diff is confined to the three regions.

Anything less is an unverified edit to the script that gates credential exposure, and the whole reason
this spec exists is that a plausible-looking build script shipped secrets for months.
