# ATOMIC SPEC — BUG-57 (remaining scope): the MailPoet vector

**Parent bug:** BUG-57 — re-scored HIGH / CONTAINED on 2026-08-28 (S135).
**This spec covers the ONLY remaining open item.** CAPTCHA was dropped as redundant; user notification
was placed out of scope. Both are operator decisions recorded in the bug entry — **do not re-raise them.**
**Created:** 2026-08-28 (S135) · **Type:** investigation, not implementation
**Gate:** operator has MailPoet admin access (confirmed S135). No further blocker.

---

## 0. WHY THIS IS STILL OPEN

62,000 accounts were created between June and August 2026. The registration form was one confirmed
vector and is now closed by BUG-63's device gate. **MailPoet was a second confirmed vector and nobody
ever established how it was accessed.**

That matters because **the two are independent**. A compromised MailPoet credential, an exposed API key,
or an auto-create-user setting is untouched by the device gate. Closing BUG-57 on the device gate alone
would be closing it on half the evidence.

⚠ **The precedent for getting this wrong is inside this very bug.** S121 recorded the registration vector
as "closed" by a WordPress setting that BUG-63 later proved was a no-op. The form stayed open for nine
days while the record said otherwise. **Do not repeat that here: no MailPoet control is "confirmed"
until it has been observed, not configured.**

---

## 1. THE THREE QUESTIONS

Answer all three. Any one of them can change the conclusion.

| # | Question | Why it matters |
|---|---|---|
| **Q1** | What do MailPoet's subscriber **import logs** show for 2026-06-01 → 2026-08-31? Bulk events, timestamps, source IP, method (API vs form vs CSV)? | Establishes *how* and *when*. Without it the root cause stays a hypothesis. |
| **Q2** | Do any **MailPoet API keys** exist, and are they exposed or unrotated? | An exposed key is a live vector today, independent of everything already fixed. |
| **Q3** | Is **"auto-create a WordPress user when an email is added to a list"** enabled? | ⚠ **The decisive one.** If yes, the 62,000 accounts may never have touched `/register/` at all — and **BUG-63's device gate does not close this path.** |

**If Q3 is yes, BUG-57 is not contained and must be re-scored upward again.** Answer Q3 first.

---

## 2. OPERATOR STEPS — click-by-click

*(Windows GUI rule: no terminal, no SSH, no command line. Browser only.)*

### Step 1 — Q3 first: the auto-create setting

1. Open your browser and go to **`https://atmyboat.com/wp-admin/`**
2. Log in as admin (2FA will prompt — that is BUG-69's fix working)
3. In the **left-hand black menu**, click **MailPoet**
4. Click **Settings**
5. Click the **Advanced** tab along the top
6. Scroll and look for a setting worded like **"Create a WordPress user"**, **"Sign-up confirmation"**,
   or **"Subscribe in comments / registration form"**
7. **Screenshot the whole tab** — do not just note the one toggle. Adjacent settings matter.
8. **Do not change anything yet.** Send the screenshot first.

### Step 2 — Q1: the import logs

1. Still in **MailPoet**, click **Subscribers** in the left menu
2. Look along the top for a **Logs** tab, or go to **MailPoet → Help → System Status / Logs**
3. Set the date range to **1 June 2026 → 31 August 2026**
4. Look for **bulk import** or **subscriber added** events — anything showing hundreds or thousands at once
5. Click into one bulk event and **screenshot the detail** — it should show a source IP and a method

If no Logs tab exists in your MailPoet version, say so — we fall back to Q1b below.

### Step 3 — Q1b (only if Step 2 finds no log)

1. Go to **MailPoet → Subscribers**
2. Click the **Filter** / **Advanced search** control
3. Filter by **Subscribed on** between 1 June and 31 August 2026
4. Note the **total count** shown
5. Screenshot the first page of results — we are looking at the **name and email patterns**

⚠ Compare that count against the ~62,000 WordPress accounts. **If the MailPoet count is much lower, the
accounts did not come in through MailPoet** and the "MailPoet was exploited" premise in the S121 record
is itself wrong — which would be worth knowing.

### Step 4 — Q2: API keys

1. Go to **MailPoet → Settings → Advanced**
2. Find the **MailPoet Sending Service / MSS key** and any **API key** field
3. **Do not paste any key into this chat.** Report only: *how many keys exist*, and *whether each shows
   as active*.
4. Also check **WordPress → Plugins** for any plugin that integrates with MailPoet (form builders,
   CRM connectors) — screenshot the plugin list

---

## 3. CLAUDE-SIDE STEPS — only after the operator's answers

**Nothing in this section may run before Step 1's screenshot.** Do not probe, do not guess, do not
write a fix for a vector that has not been confirmed.

| # | Action | Condition |
|---|---|---|
| C1 | Cross-check the WP `wpax_users.user_registered` distribution against the MailPoet subscribe dates | needs a DB read — the working credentials are `atmyb197_wp5888` per S134 |
| C2 | If Q3 = **yes**: re-score BUG-57 upward, log the auto-create path as a **new bug**, and spec the disable | Q3 answered yes |
| C3 | If Q2 shows an unrotated key: spec the rotation, including every consumer of that key | Q2 answered |
| C4 | If Q1 shows an API-based import: identify the endpoint and check whether it is still reachable | Q1 answered |
| C5 | Write the root-cause section of BUG-57 from the evidence, then close or re-score | all three answered |

⚠ **C1 needs a live database read.** `atmyb197_wp302` credentials are known broken (S134);
`atmyb197_wp5888` works. Confirm before assuming either.

---

## 4. TESTS / EXIT CRITERIA

This is an investigation, so the "tests" are evidential rather than automated.

| # | Criterion | Pass condition |
|---|---|---|
| E1 | Q1 answered | A dated log entry or a subscriber-count figure exists in the bug record, with a screenshot referenced |
| E2 | Q2 answered | Key count and status recorded; rotation specced if needed |
| E3 | Q3 answered | The setting's state recorded **from a screenshot**, not from memory or inference |
| E4 | Root cause stated | Written from evidence, with every remaining inference explicitly labelled `[UNVERIFIED]` |
| E5 | If any new vector found | Logged as its own BUG-XX **before** any fix (standing rule) |
| **E6** | **No control is described as "confirmed" without an observation** | Re-read §0. This is the specific failure this bug already suffered once. |

---

## 5. DEFINITION OF DONE

- [ ] Q3 answered first, from a screenshot
- [ ] Q1 and Q2 answered
- [ ] BUG-57 root-cause section rewritten from evidence
- [ ] Any new vector logged as a new BUG-XX before being fixed
- [ ] BUG-57 either closed, or re-scored with the reason stated
- [ ] `V09994_BUG_FIXES.md` **and** PART 17 updated together — they have contradicted each other before

---

## 6. OUT OF SCOPE — do not re-raise

- **CAPTCHA on `/register/`** — closed as redundant behind the device gate, operator decision S135.
- **Notifying the 62,000 address holders** — out of scope for v0.9.9.4, operator decision S135.
  ⚠ Recorded as *out of scope*, **not** as *resolved*. Nothing in this spec constitutes advice that no
  notification obligation exists.
- **The registration form itself** — BUG-63, closed and live. Do not reopen it here.
- **Attacker IP blocking** — BUG-67, ongoing monitoring, separate entry.
