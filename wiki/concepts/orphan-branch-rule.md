# Concept: Orphan Branch Rule

*Last updated: S86 2026-05-21 | Sources: MEMORY.md S55f*

---

## The Problem

Local `main` in the Helm-OS repo contains everything: all source code, session logs, internal docs, credential references, architecture notes, and 300+ files that must never be public. The public GitHub repo (`SkipperDon/d3kOS`) must contain only a curated set of ~12 public files.

A normal `git push origin main` would expose all internal content. This rule makes that impossible.

---

## The Rule

**NEVER push `main` to `SkipperDon/d3kOS`.** Always use the orphan branch procedure.

---

## Procedure (every public release)

```bash
# 1. Create orphan branch — no history, no connection to main
git checkout --orphan public-release

# 2. Remove everything from staging area
git rm -rf .

# 3. Add ONLY the public files (currently ~12 files + assets)
git add README.md LICENSE <public files only>

# 4. Commit
git commit -m "Public release vX.X.X"

# 5. Force push this orphan as GitHub's main
git push origin public-release:main --force

# 6. Clean up orphan branch locally
git checkout master
git branch -D public-release
```

---

## Why Force Push Is Acceptable Here

`public-release:main` rewrites GitHub's main each time. This is intentional — GitHub main has NO shared history with local main. It is a curated snapshot, not a branch anyone should ever pull from to develop.

---

## Current Public File Count

After S55f cleanup: **12 public files + assets**. 300+ internal files removed from GitHub history. GitHub repo (`SkipperDon/d3kOS`) contains only the boater-facing README and necessary public assets.

---

## Related

- [[entities/atmyboat-website]] — GitHub public repo links from site
- [[entities/d3kos-platform]] — the product published to GitHub
