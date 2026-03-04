# d3kOS Development Workflow — Cost-Optimised

## The Problem We Solved

Each Claude session was costing $30-40 because Claude was writing all the code.
Claude should write **specs and plans**. Ollama should write **code**.

Target cost per feature: **$3-5 Claude** (planning + review) + **$0 Ollama** (code generation).

---

## Roles

| Role | Who | Cost |
|------|-----|------|
| Goal → Spec → Phase config | Claude | ~$2 (short session, no code output) |
| Code generation (file edits) | Ollama via executor | $0 |
| Deploy + verify | Claude | ~$2 (read logs, run curl tests) |

---

## Session Types

### Type 1 — Planning Session (cheap, ~$2)
**Goal:** Produce a spec and phase config. No code written by Claude.

1. User describes the feature in 1–2 sentences
2. Claude reads only what it needs (targeted grep/glob, not full files)
3. Claude writes `feature_spec.md` — what Ollama must implement, with exact FIND_LINE anchors
4. Claude writes `phases.json` — one entry per file to modify
5. Claude commits both files
6. Session ends

### Type 2 — Execution (free)
**Goal:** Ollama writes the code.

```bash
cd /home/boatiq/Helm-OS/deployment/scripts
python3 ollama_execute_v3.py /home/boatiq/Helm-OS/deployment/features/<feature>/ --apply
```

Run this yourself. Takes 2–10 minutes. No Claude needed.

### Type 3 — Deploy + Review Session (cheap, ~$2)
**Goal:** Check Ollama output, deploy to Pi, verify.

1. Claude reads Ollama-modified source files (they're local after --apply)
2. Claude SCPs to Pi, restarts services, runs curl tests
3. Claude fixes any issues (usually small — wrong variable name, missed import)
4. Claude commits final result

**Total per feature: ~$4-5 instead of $40**

---

## Spec Writing Rules (what makes Ollama succeed)

Bad spec → Ollama hallucinates. Good spec → Ollama auto-applies first try.

**ALWAYS include in the spec:**

1. **Exact FIND_LINE anchors** — copy the literal line from the source file that Ollama inserts after/before. No paraphrasing.

2. **Variable names already in the file** — list them. Ollama must not invent names.

3. **Port numbers and URLs** — e.g. "use `/camera/list` not `/camera/status`"

4. **Which action** — `INSERT_AFTER`, `INSERT_BEFORE`, or `REPLACE`

5. **One change per phase** — one phase per file. Do not ask Ollama to touch 3 files in one phase.

**Spec format for each phase:**

```markdown
## PHASE N: <description> — <filename>

**File:** `<filename>`
**Action:** INSERT_AFTER / REPLACE
**FIND_LINE:** `<exact verbatim line from the file>`

**What to insert/replace:**
<clear English description of the code to write>

**Variables already in scope (use these exact names):**
- `cameras` — array from fetch('/camera/list')
- `cam.id`, `cam.name`, `cam.connected`, `cam.ip`, `cam.active`

**Do NOT:**
- Invent new fetch endpoints
- Add imports that aren't in the file
- Change anything outside the specified location
```

---

## Generic Executor

`deployment/scripts/ollama_execute_v3.py` — reads `phases.json` from any feature directory.

```bash
# Run a specific phase (dry run):
python3 ollama_execute_v3.py /path/to/feature/ settings

# Run all phases with auto-apply:
python3 ollama_execute_v3.py /path/to/feature/ all --apply

# Re-run with saved Ollama output (no new API call):
python3 ollama_execute_v3.py /path/to/feature/ all --skip-ollama --apply
```

`phases.json` schema:
```json
[
  {
    "name": "phase_name",
    "source_file": "settings.html",
    "spec_section": "PHASE 1: ...",
    "keywords": ["function updateCameraStatus", "camera1-status"]
  }
]
```

---

## RAG Before Claude

Before opening a new Claude session to understand existing code, run RAG first:

```bash
cd /home/boatiq/rag-stack
.venv/bin/python3 query.py "how does camera_stream_manager work" --collection helm_os_source
.venv/bin/python3 query.py "camera status endpoint response format" --collection helm_os_source
```

RAG answers cost $0. Only open Claude if RAG doesn't have enough.

---

## Re-ingest After Each Deploy

After deploying changed Pi source files, re-ingest so RAG stays current:

```bash
cd /home/boatiq/rag-stack
.venv/bin/python3 helm_os_ingest.py --collection source
```

---

## Cost Checklist (before opening Claude)

- [ ] Have I checked RAG first?
- [ ] Is the spec written and committed?
- [ ] Have I run Ollama already?
- [ ] Am I opening Claude only to deploy/verify, not to write code?
