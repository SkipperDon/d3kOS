# ATMYBOAT.COM — CLAUDE CODE STANDING INSTRUCTION v2.0

**Paste this entire document at the top of every Claude Code session before describing the task.** **Save this file as `ATMYBOAT\\\_STANDING\\\_INSTRUCTION.md` for quick access.**

## PLATFORM AT A GLANCE

**AtMyBoat.com** is a live WordPress website on HostPapa Growth shared hosting. Two sections are being added: a community forum at `/forum` (bbPress) and a product hub at `/products` (WordPress pages). d3kOS is product \#1. An AI assistant powered by the Gemini 2.5 Flash API lives inside the forum. Everything is built and tested on **HostPapa Staging** before a single file on the live site is touched.

| Field | Value |
| - | - |
| Live site | atmyboat.com — WordPress, Twenty Twenty theme |
| Hosting | HostPapa Growth — shared hosting, cPanel, PHP/MySQL |
| Build environment | HostPapa Staging — identical to live, one-click push |
| Forum | bbPress plugin — atmyboat.com/forum |
| Product Hub | WordPress pages — atmyboat.com/products |
| AI Assistant | PHP + cURL, Gemini 2.5 Flash API, child theme plugin file |
| SEO | Yoast SEO (installed) + Site Kit (connected to Google) |
| Email | MailPoet (installed) — uses HostPapa email server |
| Backup | UpdraftPlus (installed) — run before every migration step |
| Owner | Donald Moskaluk — [skipperdon@atmyboat.com](mailto:skipperdon@atmyboat.com) |
| GitHub | github.com/SkipperDon/atmyboat-forum |


## EXISTING PLUGINS — ALREADY INSTALLED, DO NOT REPLACE

- **MailPoet** — forum notification emails. Configure, do not reinstall.

- **Yoast SEO** — sitemap, meta tags, Open Graph. Configure, do not add competing SEO plugins.

- **Site Kit by Google** — already connected to Google Search Console. Do not disconnect.

- **UpdraftPlus** — backups. Never suggest deleting or replacing this.

- **WPReset** — staging resets only. Never suggest running this on the live site.

## BEFORE WRITING ANY CODE

1. Review `github.com/SkipperDon/atmyboat-forum` — check what already exists before creating any file

2. Check URL structure (Part 9 of `ATMYBOAT\\\_BUILD\\\_REFERENCE.md`) before adding any URL

3. All work happens on **staging only** — the live site is not touched until Phase 4

4. What is required is a seperate private for the website and mobile site.  This is proprietary information and should not be shared with the public. Recommend a site under github SkipperDon and move any information from d3kOS to this new site and remove web this site.

## ARCHITECTURE RULES — NON-NEGOTIABLE

**Theme:** Twenty Twenty with child theme at `/wp-content/themes/twentytwenty-child/`. All custom code goes in the child theme only. Never touch the parent theme.

**AI is PHP + cURL only.** File: `twentytwenty-child/inc/ai-assistant.php`. No Node.js. No npm. No PM2. This is shared hosting.

**Config from atmyboat-config.php.** All API keys via PHP `define()` constants. Never hardcode keys. File path: `twentytwenty-child/inc/atmyboat-config.php`. This file is in `.gitignore` and must never be committed.

**Gemini 2.5 Flash model only.** Gemini 2.5 Flash`\\\_MODEL = '`Gemini 2.5 Flash 

**No query text storage.** Never store user question text. Log token counts and timestamps only.

**No subdomains.** All new content is at atmyboat.com/subfolder — never forum.atmyboat.com or community.atmyboat.com. Subdomains lose SEO domain authority.

**Never suggest:** Node.js, npm, PM2, Composer, root/sudo commands, or server-side processes that require persistent execution. This is shared PHP hosting.

**Never modify** any file outside `/forum`, `/products`, `/blog`, or the child theme until Phase 4 push.

## DESIGN SYSTEM (apply to all new UI)

```
/\\\* Backgrounds \\\*/    
--bg-deep:       \\\#0A2342;   /\\\* Navy deep \\\*/    
--bg-surface:    \\\#0F2D50;   /\\\* Workbench surface \\\*/    
--bg-card:       \\\#162B47;   /\\\* Cards \\\*/    
--bg-raised:     \\\#1C3558;   /\\\* Elevated / hover \\\*/    
    
/\\\* Brand \\\*/    
--amber:         \\\#B87800;   /\\\* Primary CTA, headings \\\*/    
--amber-bright:  \\\#D4920F;   /\\\* Hover state / amber on dark \\\*/    
--teal:          \\\#1A7A6E;   /\\\* AI features, tags \\\*/    
--teal-bright:   \\\#22A090;   /\\\* Teal on dark backgrounds \\\*/    
    
/\\\* Text \\\*/    
--text-primary:  \\\#F0EAD8;   /\\\* Warm cream — 14.8:1 on bg-deep ✓ \\\*/    
--text-secondary:\\\#C8BEA8;   /\\\* 8.4:1 ✓ \\\*/    
--text-muted:    \\\#8A8070;   /\\\* 4.5:1 ✓ AA large text \\\*/    
    
/\\\* Fonts \\\*/    
--font-display: 'Playfair Display', Georgia, serif;    
--font-body:    'Source Serif 4', Georgia, serif;    
--font-mono:    'JetBrains Mono', 'Courier New', monospace;
```

**AODA rules — enforced on every component:**

- Minimum **18px body text**, **1.8 line-height** for all forum post content

- Minimum **48×48px touch targets** for all interactive elements

- Skip-to-content link as **first focusable element** on every page

- All colour pairs must pass **WCAG 2.0 AA 4.5:1** minimum contrast

## DEPLOYMENT PIPELINE — NO SSH ON HOSTPAPA

HostPapa shared hosting has **no SSH**. All deployment is via FTPS or cPanel Git VC.

**How Claude Code deploys:**

1. Writes all files locally in the `atmyboat-forum/` repo

2. Runs `deploy/sync-staging.sh` — an `lftp` FTPS sync to the staging server

3. You test in browser at the staging URL

4. Claude Code commits and pushes to GitHub

5. You click **Push to Live** in HostPapa cPanel Staging — never Claude Code

**The two deploy scripts Claude Code uses:**

```
\\\# deploy/sync-staging.sh  — Claude Code runs this automatically after each phase    
lftp -e "set ftp:ssl-force true; open -u $FTP\\\_USER,$FTP\\\_PASS $FTP\\\_HOST;    
  mirror --reverse --delete --verbose ./wp-content /public\\\_html/wp-content; bye"
```

Credentials live in `.env` (gitignored). Claude Code reads `.env` and never asks you to paste credentials into chat.

**What requires your hands (not Claude Code):**

- Installing plugins: WP Admin → Plugins → Upload ZIP

- Running one-time PHP setup scripts: Claude Code writes them, you visit the URL once, then delete

- Importing SQL: phpMyAdmin → Import (for bbPress seeds, test data)

- Promoting staging to live: cPanel → Staging → Push to Live

- Gemini 2.5 Flash key: paste into `atmyboat-config.php` locally — never in chat

**Cannot do on HostPapa (no SSH):** `wp-cli` · `composer` · `npm` · `crontab` · `rsync` · recursive `chmod` from terminal All have workarounds documented in ATMYBOAT\_BUILD\_REFERENCE.md Part 15.

## WHAT CLAUDE CODE MUST NEVER DO

- Modify any file outside `/forum`, `/products`, `/blog`, or the child theme

- Suggest Flarum, a separate forum subdomain, or any separate forum server

- Suggest Node.js, npm, or anything requiring server-level package management

- Change to Claude Sonnet or any model other than claude-haiku-4-5-20251001

- Increase Gemini 2.5 Flash `MAX\\\_TOKENS` above 1000

- Log or store user question text in any form

- Hardcode the Gemini API key anywhere

- Commit `atmyboat-config.php` or `.env` to GitHub

- Run WPReset on the live site

- Deploy directly to live — staging first, always

- Attempt SSH, WP-CLI, composer, or npm — HostPapa blocks all of these

- Push anything to live without a verified UpdraftPlus backup taken first

## AT THE END OF EVERY SESSION

Claude Code must provide:

1. **Commit summary:** Every file changed and what it does

2. **Deployment steps:** Exact `lftp` sync command and what to test on staging

3. **Manual steps for you:** Any plugins to install, SQL to import, PHP scripts to run

4. **Next session:** Which phase sub-task comes next and what context to bring

5. **New config constants:** Any new `define()` needed in `atmyboat-config.php` with the value source

6. **Version table row:** What to add to Part 14 of `ATMYBOAT\\\_BUILD\\\_REFERENCE.md`

## COST REMINDER

Solo bootstrap. gemini only. Hard cap set in geminiConsole. Check if something already exists before building it. One complete session beats three partial ones.

## CURRENT PHASE STATUS

*(Update this section at the start of each session based on your version table)*

| Phase | Status |
| - | - |
| Phase 0 — Staging activated, backup verified | ☐ Pending |
| Phase 1 — Child theme active on staging | ☐ Pending |
| Phase 2A — bbPress forum + MailPoet | ☐ Pending |
| Phase 2B — AODA design applied | ☐ Pending |
| Phase 2C — PHP AI assistant | ☐ Pending |
| Phase 2D — Product hub | ☐ Pending |
| Phase 2E — SEO configuration | ☐ Pending |
| Phase 2F — Mobile app backend (command queue, pairing, Stripe, PDF reports) | ☐ Pending |
| Phase 3 — AODA compliance audit | ☐ Pending |
| Phase 4 — Migration staging → live | ☐ Pending |


\*AtMyBoat.com Standing Instruction v2.0 · Donald Moskaluk · [skipperdon@atmyboat.com\*](mailto:skipperdon@atmyboat.com) *Full reference: ATMYBOAT\_BUILD\_REFERENCE.md*

