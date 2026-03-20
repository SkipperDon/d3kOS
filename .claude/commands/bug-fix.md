## Bug Fix — AAO Compliant Workflow

Follow these steps in order. Do not skip any step.

1. **Reproduce** — confirm you can trigger the bug
2. **Risk classify** — apply AAO risk table before any action
3. **Write a failing test** — write a test that fails because of the bug, commit it
4. **Fix** — make the minimal code change, do not refactor unrelated code
5. **Verify** — run the full test suite, all tests must pass
6. **Lint** — run linter, zero errors required
7. **Log** — update SESSION_LOG.md: bug description, root cause, fix applied
8. **Report** — present summary in chat for Don's review
