# AtMyBoat.com v0.9.3 — Session Log

---

## Session — 2026-03-13 — Staging Activation, FTP Access, Font Size Pass

**Goal:** Get staging products page working and fonts readable for 45–70 year old users.

**Completed:**
- Established working FTP access via `d3kos@atmyboat.com` (previous `cool@` and `staging@` accounts chrooted to empty dirs — this account lands at `/public_html`)
- Diagnosed products page showing no content: child theme (Twenty Twenty Child) was not activated on staging WP Admin
- Activated child theme on staging — products page now renders correctly
- Fixed `atmyboat-config.php` constant name mismatch: file had `ATMYBOAT_API_KEY` but `ai-assistant.php` checks for `GEMINI_API_KEY` — corrected + added missing `GEMINI_MODEL`, `GEMINI_MAX_TOKENS` constants
- Diagnosed AI "service unavailable" error: Gemini free-tier daily quota (20 req/day) exhausted during testing — model name `gemini-2.5-flash` is correct, will reset at midnight UTC
- Font size pass — multiple iterations to override Twenty Twenty parent theme CSS:
  - Root cause: parent theme sets font sizes on specific elements, not just `body`; `rem` units resolve to browser default 16px not our 22px body
  - Fix: converted all `rem` font sizes to explicit `px`; added `!important` to body, p/li/label, buttons, tags, section-labels, AI widget label
  - body: 18px → 22px; buttons: 1rem → 20px; tags: 0.6rem → 18px; section-label: 0.65rem → 18px; AI widget label: 0.65rem → 20px; headings: clamp(rem) → clamp(px)
- All files deployed to staging via FTP (curl --ftp-ssl)

**Decisions:**
- FTP account to use going forward: `d3kos@atmyboat.com` — lands at `/public_html`, has full access. Password in use this session — change it after key rotation (see security note below)
- Gemini model stays as `gemini-2.5-flash` — it is available on this API key, just quota-limited on free tier (20/day). Daily reset at midnight UTC.
- All `rem` font sizes replaced with `px` throughout child theme CSS — ensures sizes are absolute and not affected by any parent theme `html` font-size setting
- `!important` used throughout to override Twenty Twenty parent theme — necessary given shared theme architecture on shared hosting with no ability to edit parent theme

**Files changed (repo):**
- `wp-content/themes/twentytwenty-child/style.css` — comprehensive font size overhaul (rem→px, !important overrides, body/p/buttons/tags/labels/AI widget)
- `wp-content/themes/twentytwenty-child/page-products.php` — price label inline style 1rem → 20px

**Files changed (staging server only — not in repo):**
- `staging/wp-content/themes/twentytwenty-child/inc/atmyboat-config.php` — fixed GEMINI_API_KEY constant, added GEMINI_MODEL + GEMINI_MAX_TOKENS

**⚠️ SECURITY — ACTION REQUIRED:**
- Gemini API key (`AIzaSy...hR0`) was exposed in this chat session when Claude read the server config file
- **Don must rotate this key** in Google AI Studio and update `atmyboat-config.php` on staging server
- Key is not in the git repo (file is gitignored) — no repo action needed, server-only update

**Costs:**
| Source | Metric | Cost |
|--------|--------|------|
| Claude API | Check console.anthropic.com → Usage → 2026-03-13 | TBD |
| Ollama | Not used this session | $0.00 |
| Session total | | TBD |

**Pending / Open items for next session:**
- Font sizing: Don ended session with fonts still not fully resolved on all elements — screenshot not received. Need Don to copy screenshot to `\\wsl.localhost\Ubuntu\home\boatiq\screenshot.png` and share so remaining small elements can be identified precisely
- AI widget: will work again after Gemini quota resets (midnight UTC). Test tomorrow.
- Phase 2E (SEO): Yoast/RankMath config, sitemap submission — not started
- Phase 3 (AODA audit): keyboard nav, WAVE scan, touch target check — Don's task
- Phase 4 (staging → live): Don's hands only — cPanel Push to Live — not ready yet
- FTP password rotation: change `d3kos@atmyboat.com` FTP password after Gemini key rotation
- GitHub repo `atmyboat-forum`: set to Private after live launch

**Sign-off:** Don — silence = approval

---

## Session — 2026-03-16 — Session Planning

**Goal:** Review remaining v0.9.3 work and organize into sessions.

**Completed:**
- Reviewed PROJECT_CHECKLIST.md — identified all remaining open items
- Organized remaining work into 4 sessions + post-launch
- Security key rotation deferred to Session 4 (project close) — existing keys in use until work is complete
- PROJECT_CHECKLIST.md updated with Session Plan section

**Decisions:**
- Gemini API key stays in place until project is complete — removed at Session 4 closeout
- FTP password changed at Session 4 closeout
- Session order: MailPoet+Fonts → SEO → AODA Audit → Live Push

**Ollama:** 0 calls

**Costs:**
| Source | Metric | Cost |
|--------|--------|------|
| Claude API | check console.anthropic.com → Usage → 2026-03-16 | TBD |
| Ollama | 0 calls | $0.00 |

**Files changed:**
- MOD: `deployment/v0.9.3/PROJECT_CHECKLIST.md` — Session Plan section added, security note updated
- MOD: `deployment/v0.9.3/SESSION_LOG.md` — this entry

**Pending:**
- Don to authorize Session 1 (say "go ahead" / "start session 1")

**Sign-off:** Don — silence = approval

---
