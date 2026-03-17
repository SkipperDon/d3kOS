# d3kOS — CSS Debug Guide: UAT S-06 Nav Button Rendering
**Created:** 2026-03-16 | **Status:** Ready to run
**Issue:** Nav active state, icon opacity not rendering in Pi Chromium (--disable-gpu mode)

---

## Setup — Already Done

- `--remote-debugging-port=9222 --remote-debugging-address=0.0.0.0` added to `/opt/d3kos/scripts/launch-d3kos.sh` and deployed to Pi
- Pi needs **reboot** for Chromium to pick up the new flag

**Reboot the Pi first.** Wait 45 seconds for it to come back up and Chromium to launch.

---

## Step 1 — Connect Windows Chrome to Pi DevTools

1. On the Windows laptop, open **Google Chrome** (not Edge — Chrome only)
2. In the address bar type: `http://192.168.1.237:9222`
3. You will see a page listing open tabs. One will say `d3kOS` or `localhost:3000`
4. Click **"inspect"** next to that entry
5. Chrome DevTools opens in a new window — you are now connected to the Pi's live browser

> If the page doesn't load — Pi hasn't finished booting yet. Wait 30 more seconds and refresh.

---

## Step 2 — Reload the page and check CSS is current

1. In DevTools → click the **Network** tab
2. Check the box **"Disable cache"** (top of Network panel)
3. On the Pi screen (or in DevTools → press `Ctrl+R`) reload the page
4. In the Network filter box type: `d3kos.css`
5. Click the `d3kos.css` entry → click **"Response"** tab on the right
6. Press `Ctrl+F` to search → type `nb-icon`

**You should see:**
```css
.nb-icon { font-size: 32px; line-height: 1; opacity: 0.38; }
```

**Record:** Is this text visible in the response? YES / NO

> If NO — the wrong CSS file is being served. The Pi Flask service needs restarting.
> If YES — CSS is being fetched correctly. Continue to Step 3.

---

## Step 3 — Check computed opacity on an inactive nav button icon

1. In DevTools → click the **Elements** tab
2. Click the **cursor/pick icon** (top-left of Elements panel — looks like `⊡`)
3. On the **Pi screen**, tap the **"Marine Vision"** nav button (it should be inactive — not the current page)
4. Back in DevTools → look at the highlighted element
5. Navigate UP the element tree until you find an element with class `nb-icon`
   - It will look like: `<div class="nb-icon">📷</div>` or similar emoji
6. Click the **"Computed"** tab (right panel)
7. In the Computed filter box type: `opacity`

**Record the result:**

| Expected | Actual (fill in) | Verdict |
|----------|-----------------|---------|
| `opacity: 0.38` | | |

- **If 0.38 shows** → CSS rule IS applied. Opacity is working but visually subtle. Issue is perception, not code.
- **If 1 shows** → Something is overriding the rule. Go to Step 3b.
- **If missing** → Rule not matched. Wrong element selected — try again.

### Step 3b — Find what's overriding opacity (only if Step 3 shows 1)

1. With the `.nb-icon` element still selected → click **"Styles"** tab (right panel)
2. Look for `opacity` entries
3. Rules that are **crossed out** are overridden
4. Note which rule is winning (what class/selector is setting opacity: 1)
5. **Record the winning selector here:** ___________________

---

## Step 4 — Check active background on Dashboard button

1. Pick element → tap the **"DASH"** nav button on Pi screen (this should be the active/highlighted one)
2. Navigate UP in Elements to find `<button class="nb ... nb-active ...">` or `<div class="nb ... nb-active">`
3. Computed tab → filter: `background-color`

**Record the result:**

| Expected | Actual (fill in) | Verdict |
|----------|-----------------|---------|
| `rgba(0, 90, 0, 0.22)` | | |

- **Matches** → background is working
- **Shows white / transparent** → `.nb.nb-active:not(.helm)` rule not applying. Go to Step 4b.

### Step 4b — Check if nb-active class is present

1. With the Dashboard button still selected in Elements tab
2. Look at the class attribute at the top of the element panel
3. Does it say `nb-active` in the class list? YES / NO

- **NO** → The JS isn't setting the active class. Different problem (JS, not CSS).
- **YES** → Specificity conflict. Another rule overrides the background. Note which one.

---

## Step 5 — Check active indicator bar (5px bottom bar)

1. With the Dashboard `.nb.nb-active` button selected in Elements
2. In the Elements tree, click the **▶** arrow to expand it
3. Look for a `::after` pseudo-element in the tree
4. Click it → Styles tab → look for `height: 5px` and `background: var(--g-txt)`

**Record:** Is the `::after` visible and styled? YES / NO

---

## Step 6 — Check Night mode / data-night attribute

1. In the Elements tree, navigate ALL the way up to the `<html>` element
2. Look at its attributes — does it have `data-night` attribute?

**Record:** `data-night` present? YES / NO

> If YES and the page is in night mode — day-mode CSS token values won't apply.
> This would explain why `rgba(0,90,0,0.22)` (day green) looks invisible on a black background.

---

## What to do with results

Once all steps recorded, return this document (or paste the results into chat).
Claude will interpret the findings and deliver the exact fix — targeted, not exploratory.

**Fastest path:** Take a photo of the DevTools window showing the Computed panel for Steps 3 and 4.
Post the photo in the chat. Same result.

---

## CSS rules being diagnosed (for reference)

```css
/* Currently deployed in d3kos.css ?v=16 on Pi */

/* Inactive nav icons — should appear at 38% opacity */
.nb-icon { font-size: 32px; line-height: 1; opacity: 0.38; }

/* Active nav icons — full opacity */
.nb.on .nb-icon, .nb.nb-active .nb-icon { opacity: 1; }

/* Active non-HELM button — visible green background */
.nb.nb-active:not(.helm), .nb.on:not(.helm) { background: rgba(0,90,0,0.22); }

/* Active indicator bar — 5px at bottom */
.nb.on::after, .nb.nb-active::after {
  content: ''; position: absolute;
  bottom: 0; left: 0; right: 0; height: 5px;
  background: var(--g-txt);
}
```

---

*Document: deployment/d3kOS/docs/CSS_DEBUG_GUIDE.md*
*Pi: --remote-debugging-port=9222 active after next reboot*
