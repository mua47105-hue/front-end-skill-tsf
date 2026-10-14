# Spoke 05: QA & Blind Creative Critic (The Gauntlet Loop)

**Load this file only when you are running Stage 6.**

Stage 6 is where the studio stops believing itself. Two independent passes:

1. A **machine pass**: a headless browser proves the runtime is clean.
2. A **blind pass**: a critic who cannot see your labels compares your render
   against the Stage 2 Reference Bar and finds the thing that makes it generic.

Both passes must pass. A clean console with a boring page is a failure.

## 1. Step 1: Automated Runtime & Viewport Verification

### 1.1 Install (once)

```bash
npm init -y
npm install -D playwright
npx playwright install chromium
```

### 1.2 Run the gauntlet inspector

```bash
node skills/frontend-studio-gauntlet/scripts/playwright_gauntlet.js \
  --url ./index.html \
  --out .studio/screenshots
```

Useful flags: `--timeout 30000` (per-viewport budget in ms), `--viewport-only`
(viewport screenshots instead of full page), `--headed` (watch it run while
debugging).

If the script cannot import Playwright it prints the exact install command and
exits 2. That is a `BLOCKED` state, never a `WIN`.

### 1.3 What the inspector proves

| Check | Pass condition | Why it matters |
| --- | --- | --- |
| Console errors | 0 `console.error` entries | silent runtime failures |
| Page errors | 0 uncaught exceptions | broken handlers |
| Horizontal overflow | `documentElement.scrollWidth <= window.innerWidth` | the mobile scroll-jank tell |
| Broken images | every `<img>` has `complete && naturalWidth > 0` | empty hero art |
| Step activation | every `[data-step]` reaches active state on scroll | broken scrollytelling |
| Interactive hero input | pointer and click into `[data-interactive-hero]` raise 0 new errors | an instrument that only works untouched is broken |
| Frame stability | at most 2 of 20 sampled frames exceed 50ms | a render loop that never sleeps |
| Design spells | 2 or more `data-spell` elements when a hero instrument exists | unnamed delight reads as noise |

Two contexts run every check:

- **Desktop 1440x900**: the design viewport. Judge composition here.
- **Mobile 390x844**: iPhone-class. Judge overflow, tap targets, and type
  reflow here.

Both screenshots are written as `desktop-1440x900.png` and
`mobile-390x844.png` inside `--out`.

### 1.4 Manual sweep the script cannot do

The script is a floor, not a ceiling. Add these by hand:

- Keyboard walk: `Tab` through the page. Every stop is visible and logical.
- Narrow stress: check at 360px and at 1920px, not only at 390 and 1440.
- Zoom to 200 percent. Nothing overlaps, nothing clips.
- Slow 3G. The pin engages late but never janks or snaps.
- DevTools: `Rendering` panel, emulate `prefers-reduced-motion: reduce`. The
  page still communicates everything.

## 2. Step 2: The Blind Critic Comparison Protocol

### 2.1 Strip the labels

The comparison only works if the critic cannot read your intent.

1. Screenshot your page at 1440x900 and 390x844 (done in step 1).
2. Screenshot the Primary Bar and Secondary Bar references at 1440x900.
3. Rename every file to an opaque name: `A.png`, `B.png`, `C.png`, `D.png`.
4. Do not show filenames, page titles, brand names, or the brief.

If you already know which is which, you are no longer blind. Rebuild the set.

### 2.2 The 4 Blind Critic Axes

Score each axis 1 to 10 for **your render** and for the **Primary Bar**.

#### Axis A: Unmistakable Hero Focal Point

Look at the hero for three seconds. What is the single thing you remember?

- 8 or 9: one object, one focal point, obvious in the first second.
- 5 or 6: you can name two things competing.
- 3 or 4: centered headline, centered subhead, two buttons, a screenshot.

Fail condition: the hero reads as "everything is equally important".

#### Axis B: Section Rhythm Variance

Scroll the full page at reading speed. Count the distinct layout archetypes.

- 8 or 9: five or more genuinely different sections, density alternating.
- 5 or 6: three archetypes, one repeated.
- 3 or 4: one archetype repeated end to end.

Fail condition: two adjacent sections share a layout, especially two 3-column
card rows.

#### Axis C: Typographic Tension & Hierarchy

Squint until the text blurs. Is the hierarchy still legible?

- 8 or 9: three unmistakable levels, a real display face, intentional tracking.
- 5 or 6: clear hierarchy, unremarkable type.
- 3 or 4: one weight, one size ramp, everything the same size.

Fail condition: a banned default font family with no display counterpart, or a
type scale where the hero is 1.2x the h1.

#### Axis E: Signature Interactive Hook & Tactile Craft

> "The page has a pulse." Or it does not.

Ask: if I moved the pointer, did *something specific* change, and did it feel
deliberate rather than twitchy? Then count the live Design Spells.

- 8 or 9: the hero instrument responds within 100ms of input, at least 2
  distinct `data-spell` behaviors are live and observable, and springs settle
  rather than oscillate.
- 5 or 6: exactly one interactive element, everything else static.
- 3 or 4: the hero is a screenshot and the CTAs only change hover color.

Verification method: run `playwright_gauntlet.js`, which dispatches synthetic
`pointerenter`, `pointermove`, and `click` into the first
`[data-interactive-hero]` and fails on any resulting error. Confirm by hand
that the interaction is *perceptible*, not merely error-free.

Fail conditions:

- No `data-interactive-hero` anywhere on the page.
- Fewer than 2 `data-spell="..."` elements, or spells declared but never wired.
- An animation loop that never sleeps, showing sustained CPU while idle.
- Motion that ignores `prefers-reduced-motion: reduce`.

#### Axis D: The Coco Chanel Polish Rule

> "Before you leave the house, remove one piece."

The last 5 percent is subtraction. A page that fails this axis is usually
carrying one piece of decorative chrome that the reference would not have.

Remove at least one of these in Round 1:

- A redundant border around a card that has a background.
- A shadow on a surface that already has a hairline.
- An ALL-CAPS eyebrow above every heading.
- A numbered badge on content that is not sequential.
- An arrow on every CTA.
- A second decorative rule under a section heading.

Fail condition: Round 1 removed nothing.

## 3. Step 3: Mandatory Refinement Pass

**Round 1 always finds and fixes at least one concrete defect before a `WIN` is
logged.** This is not ceremony. A page that survives first contact with a
hostile critic on the first try has not actually been critiqued.

The loop:

| Round | Action | Output |
| --- | --- | --- |
| 0 | capture screenshots, run the automated checks | raw render + machine report |
| 1 | blind comparison, score the 4 axes, find the weakest axis | findings list |
| 2 | apply at least one concrete fix, plus one Chanel subtraction | edited source |
| 3 | re-capture, re-run the checks, re-compare | before/after screenshots |
| 4 | log the round-by-round fixes and the verdict | `.studio/06-GAUNTLET-REPORT.md` |

Rules for the fix in Round 2:

- It must be **specific**: "reduce the hero meta block to two lines and align
  its baseline to the h1 cap height", not "improve spacing".
- It must be **verifiable**: after the fix, the screenshot or the automated
  check visibly changes.
- It must address the **weakest axis** from Round 1, not the easiest one.
- The automated checks are re-run after every fix. A fix that introduces
  overflow or a console error is reverted.

Honesty rule: if the render genuinely cannot be fixed in this session, log
`BLOCKED` with the reason. A fabricated `WIN` is the worst possible outcome of
this skill.

## 4. Template: `.studio/06-GAUNTLET-REPORT.md`

The gate requires `Desktop Screenshot`, `Mobile Screenshot`,
`Console / Page Errors`, `Horizontal Overflow Check`, `Reference Bar Compared`,
`Round 1 Critic Findings & Fixes Applied`, and `Final Verdict`, a `WIN` in the
verdict, and 250 characters minimum.

```markdown
# 06 Gauntlet Report

Project: <one line>
Entry under test: <path or URL>
Command: node skills/frontend-studio-gauntlet/scripts/playwright_gauntlet.js --url <url> --out .studio/screenshots

## Desktop Screenshot

- Viewport: 1440x900
- File: .studio/screenshots/desktop-1440x900.png
- Page height at capture: <px>
- First-viewport focal point: <what lands in the first 300ms>

## Mobile Screenshot

- Viewport: 390x844
- File: .studio/screenshots/mobile-390x844.png
- Reflow notes: <what changed, did any element clip>

## Console / Page Errors

- console.error count: <n>
- pageerror count: <n>
- Broken images: <n of m>
- Hero interaction errors (+errors from pointer input): <n>
- Jank frames (of 20 sampled, over 50ms): <n>
- Details: <exact text of every error, or "none">

## Horizontal Overflow Check

| Viewport | innerWidth | scrollWidth | Pass |
| --- | --- | --- | --- |
| 1440x900 | <n> | <n> | yes/no |
| 390x844 | <n> | <n> | yes/no |

## Scrollytelling Step Activation

| Step | Reached active state | Active selector observed |
| --- | --- | --- |
| step-01 | yes/no | is-active |
| step-02 | yes/no | is-active |
| step-03 | yes/no | is-active |
| step-04 | yes/no | is-active |

Activation rate: <n>/<n>

## Reference Bar Compared

- Primary Bar: <name, URL>
- Secondary Bar: <name, URL>
- Comparison performed with labels stripped: yes

| Axis | Our render | Primary Bar | Gap | Verdict |
| --- | --- | --- | --- | --- |
| A. Hero focal point | <1-10> | <1-10> | <n> | pass/fail |
| B. Section rhythm variance | <1-10> | <1-10> | <n> | pass/fail |
| C. Typographic tension | <1-10> | <1-10> | <n> | pass/fail |
| D. Coco Chanel polish | <1-10> | <1-10> | <n> | pass/fail |
| E. Interactive hook & tactile craft | <1-10> | <1-10> | <n> | pass/fail |

### Interactive Hook Verification

| Check | Result |
| --- | --- |
| `data-interactive-hero` count | <n> |
| `data-spell` element count | <n> |
| Distinct spell names | <names> |
| Pointer input produced a visible change | yes/no |
| Keyboard input produced a visible change | yes/no |
| Springs settle, no oscillation | yes/no |
| Idle CPU returns to zero | yes/no |
| Reduced motion yields a still frame | yes/no |

## Round 1 Critic Findings & Fixes Applied

Weakest axis: <A|B|C|D>

| # | Finding | Fix applied | Evidence | Rerun checks |
| --- | --- | --- | --- | --- |
| 1 | <concrete defect> | <specific change> | <file + screenshot> | pass/fail |
| 2 | <chanel subtraction: chrome removed> | <what was removed> | <file + screenshot> | pass/fail |

Round 2 re-capture: <desktop/mobile filenames after fixes>
Automated checks after fixes: console <n>, pageerror <n>, overflow <pass/fail>

## Final Verdict

Verdict: <WIN | BLOCKED>

<One paragraph: why this passes the bar, and which axis improved most. If
BLOCKED, state exactly what could not be verified and why.>
```

## 5. Final Gate

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase 6 --dir .studio --target <entry-file-or-src-dir>
```

The run must print:

```text
GATE 6 PASSED: ALL FRONTEND STUDIO CRITERIA VERIFIED
```

Report that line verbatim. Until it appears, the work is not finished.
