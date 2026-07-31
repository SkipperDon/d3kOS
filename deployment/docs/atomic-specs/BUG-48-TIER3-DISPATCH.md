# BUG-48 — Tier 3 Dispatch Prompt

Paste everything below the line into the Tier 3 implementer
(Ollama `devstral:24b` at `192.168.1.36:11434`).

**Do not paraphrase it.** The constraints are the point.

---

TASK TYPE: [IMPLEMENT] — Tier 3

You are the Tier 3 implementer on d3kOS v0.9.9.4. Tier 1 (Opus) wrote your spec
and will verify your work under AAO §25.8. Do exactly what the spec says and
nothing more. You are not being asked to design anything.

WORKING DIRECTORY: /home/boatiq/Helm-OS
Run all node and npx commands from that directory (node_modules lives there).

PRE-EDIT SNAPSHOT — PRE-CLEARED, DO NOT HALT
Your baseline is commit c8ef88a. The working tree has exactly two untracked
entries that are NOT yours:
    deployment/docs/atomic-specs/BUG-48.md   (your spec — read it, never edit it)
    test-results/                            (Playwright output, ignore)
The operator has acknowledged these and authorises you to proceed. Do not touch
them, do not commit them, do not mention them again.

READ THIS FILE FIRST, IN FULL, BEFORE TOUCHING ANYTHING
    deployment/docs/atomic-specs/BUG-48.md
It contains the exact edit table (Groups A, B, C), the required URL pattern, the
guard test to write, and the special cases A4, A9 and B6. Every line number and
content string in it was verified against the repo on 2026-07-31.

YOUR TASK — BUG-48 ONLY
Replace every hardcoded `localhost` service URL in the dashboard front-end with
the page-derived form:
    'http://' + window.location.hostname + ':<PORT>' + '<path>'
Groups A and B of the spec table. That is 18 call sites across 11 files, all
inside:
    deployment/v0.9.9.4/opt/d3kos/services/dashboard/
Do not start BUG-47, BUG-15, or any other bug. One bug at a time.

HARD CONSTRAINTS
- Edit ONLY inside deployment/v0.9.9.4/opt/d3kos/services/dashboard/.
- NEVER write to deployment/v0.9.4/pi_source/ or d3kOS/dashboard/. Both are
  SUPERSEDED read-only reference trees.
- Do NOT change any port number. Ports stay exactly as they are in the table.
- Do NOT change any path or query string.
- Do NOT touch templates/index.html line 191 (`{{ avnav_port }}`). It is
  server-rendered Jinja and is explicitly OUT OF SCOPE.
- Do NOT change the Group C operator-facing error strings. They mention
  localhost in user-visible copy; changing copy needs operator approval.
- Do NOT create a helper module, a config endpoint, or use
  window.location.origin. Use the exact pattern above — it is the one already
  established by BUG-34 and BUG-46.
- Do NOT touch the Pi. No ssh, no scp, no systemctl. Tier 1 deploys.
- Do NOT commit. Leave your changes in the working tree.
- Do NOT regenerate MANIFEST.md5.

TDD — MANDATORY SEQUENCE, NO SHORTCUTS
1. Write tests/bug48-no-hardcoded-localhost.spec.ts exactly as given in the spec.
2. RUN IT. Paste the real terminal output:
       export LD_LIBRARY_PATH="$HOME/.local/pw-libs/root/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
       BASE_URL=http://192.168.1.237:3000 npx playwright test tests/bug48-no-hardcoded-localhost.spec.ts --reporter=list
   It MUST FAIL and list the hardcoded URLs. Tier 1 confirmed this is the current
   deployed state. If it PASSES, STOP and escalate — you are testing the wrong
   target.
3. Only then make the edits.
4. Run the Step 4 grep and the Step 5 `node --check` loop from the spec. Paste
   the real output of both.

Note: the guard test runs against the DEPLOYED lab Pi, which Tier 1 has not
updated with your edits. It will still fail after step 3. That is expected. Step
4's grep is your proof, not the test re-run.

Do not write the fix first. Do not claim a run you did not perform. If you did
not paste real terminal output, the work is rejected.

IF YOU ARE UNSURE ABOUT ANYTHING
Do not guess and do not invent a default. File a question at
wiki/questions/2026-07-31-<slug>.md, add a pointer in wiki/index.md, record your
provisional assumption, and continue with the other edits. Never assume on
anything touching a port number or a path.

WHEN DONE, RETURN
1. `git diff --stat` — expect ~11 files, roughly 18 insertions / 18 deletions.
   If deletions exceed insertions you have removed something. Stop and say so.
2. Full `git diff` for static/js/panel-toggle.js and
   templates/manage-documents.html — these contain the two trickiest edits
   (A9 keeps a `port` variable; B6 is a template literal needing
   `${window.location.hostname}`, not concatenation).
3. The failing step-2 output, the step-4 grep output, and the step-5 syntax output.
4. Decision Log: every deviation from the spec, or the single word "none".

---

## What Tier 1 checks when it comes back

Watch for these three failure modes specifically:

1. **A changed port number.** Diff every `:<port>` against the spec table. A
   silently altered port produces a service that fails only at runtime, on the
   boat.
2. **B6 done with string concatenation** instead of `${window.location.hostname}`
   inside the template literal. It will look right and produce a literal
   `${...}` in the URL.
3. **Only a passing run shown.** The most common Tier 3 failure is writing the
   fix first and running the test once. If there is no failing run, the TDD
   sequence was not followed and the work is rejected regardless of the diff.

Also confirm A4 has **no** port segment, and that
`deployment/v0.9.9.4/.../templates/index.html` is untouched.

After acceptance, Tier 1 deploys to the lab Pi and re-runs all four suites —
BUG-43 (8) + BUG-46 (3) + BUG-47 (3) + BUG-48 — expecting green across the board.
