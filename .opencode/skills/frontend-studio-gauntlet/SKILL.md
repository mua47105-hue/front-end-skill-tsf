---
name: frontend-studio-gauntlet
description: This skill orchestrates a six-stage frontend design and engineering studio that produces high-craft, non-generic web surfaces. It applies to web design, landing pages, marketing sites, UI/UX redesigns, design system work, scrollytelling and data storytelling, and anti-slop frontend engineering in HTML, CSS, JavaScript, React, Next.js, Tailwind, Vue, or Svelte. Use it when asked to design, build, or critique a user-facing interface, especially when the output risks looking generic or AI-generated.
license: MIT
---

# Frontend Design & Engineering Studio (The Gauntlet)

A hub-and-spoke skill that runs a six-stage design studio and refuses to ship
until a deterministic gate proves every stage passed.

## 1. The Progressive Disclosure Contract

This file is the **Hub**. The domain rules live one level deep in
`references/`. Read them **one at a time**, never all at once.

1. Read `SKILL.md` (this file) once per project.
2. For the stage you are about to run, read **only** its single spoke file:

   | Stage | Role | Spoke to load |
   | --- | --- | --- |
   | 1 | Product Director | none (hub only) |
   | 2 | Visual Researcher | `references/spoke-01-inspiration.md` |
   | 3 | Design Systems Architect | `references/spoke-02-tokens-antislop.md` |
   | 4 | Principal UX & Motion Architect | `references/spoke-03-scrollytelling-layout.md` |
   | 5 | Senior Frontend Engineer | `references/spoke-04-implementation-craft.md` |
   | 6 | QA & Blind Creative Critic | `references/spoke-05-gauntlet-verification.md` |

3. Load a new spoke **only** when the stage unlocks. Do not preload. Do not
   quote a spoke you have not read.
4. Each spoke is non-overlapping. If two spokes seem to disagree, the spoke
   that owns the stage wins.

Every stage writes a required artifact into `.studio/` inside the **target
project workspace** (not the skill directory) and must pass the gate before the
next stage unlocks:

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase <N> --dir .studio
```

The validator is cumulative: `--phase N` re-verifies phases `1..N-1` first, so
a single `6` run re-proves the entire chain.

## 2. Completion Is a Verified Finding, Never a Claim

You are **forbidden** from saying "done", "finished", "ready", or "shipped"
before the Phase 6 gate prints this exact line:

```text
GATE 6 PASSED: ALL FRONTEND STUDIO CRITERIA VERIFIED
```

Rules that make this enforceable:

- Never narrate a gate you did not run. Run it, then quote its output.
- If a gate fails, fix the artifact, re-run the gate, and paste the new output.
- If the browser gauntlet cannot run (no Playwright, no Chromium), say so
  explicitly and mark the run `BLOCKED`, never `WIN`.
- A passing static gate is necessary but not sufficient. Gate 6 also requires
  the Blind Critic round documented in `.studio/06-GAUNTLET-REPORT.md`.

## 3. The Six Mandatory Stages

### Stage 1: Product Director (Brief & Taste Dials)

No spoke file. Decide the product in one page.

Write `.studio/01-BRIEF.md` containing:

- Target audience (specific: role, seniority, what they already know).
- Core job-to-be-done in one sentence, phrased as the user's action not the
  feature list.
- The chosen **Aesthetic Archetype** (for example: Swiss editorial, industrial
  hardware, luxury lookbook, dark precision cockpit, warm brutalist).
- Three integer **taste dials**, each an explicit integer from 1 to 10:

  | Dial | 1-3 means | 8-10 means |
  | --- | --- | --- |
  | `DESIGN_VARIANCE` | safe, familiar, low surprise | bold, idiosyncratic, surprising |
  | `MOTION_INTENSITY` | static, no scroll motion | pinned stages, scrubbed camera |
  | `VISUAL_DENSITY` | airy, lots of negative space | packed, data-rich, editorial |

- The 2-3 pages or sections that matter most, and the one conversion action.

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase 1 --dir .studio
```

### Stage 2: Visual Researcher (Inspiration & Named Quality Bar)

Read `references/spoke-01-inspiration.md`. Then actually research: browse or
search Pinterest, Awwwards, Godly, Mobbin, The Pudding, Land-book, and Design
Spells using the archetype-specific operators in the spoke.

Select 2 to 3 **Named, Fetchable, Comparable** references and write
`.studio/02-MOODBOARD.md` with the required headings from the spoke template:
`Primary Bar`, `Secondary Bar`, `Hero Treatment`, `Grid & Section Rhythm`,
`Typography Behavior`, `Color & Surface Texture`, `Image & Media Art Direction`.

Every reference needs a real URL. A named-but-unfetchable bar is a failed bar.

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase 2 --dir .studio
```

### Stage 3: Design Systems Architect (OKLCH Tokens & Anti-Slop)

Read `references/spoke-02-tokens-antislop.md`. Then create
`.studio/03-TOKENS.css` as a real, pasteable stylesheet:

- Perceptual `oklch()` colors derived from `--brand-hue` and `--accent-hue`
  (never hardcoded AI-purple hexes; the gate bans `#6366f1`, `#a855f7`,
  `#8b5cf6`).
- Fluid `clamp()` type scale: `--text-hero`, `--text-h1`, `--text-h2`,
  `--text-h3`, `--text-body`, `--text-mono`.
- Max 2 font families plus an optional tabular mono, chosen against the
  Anti-Slop Ban List.
- Spacing on a 4px/8px grid, radii, borders, shadows, and cubic-bezier easing.
- Light and dark mode via `color-scheme` and a `[data-theme]` or
  `prefers-color-scheme` block.

Audit your own tokens against the ban list before running the gate.

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase 3 --dir .studio
```

### Stage 4: Principal UX & Motion Architect (Wireframe & Beat Sheet)

Read `references/spoke-03-scrollytelling-layout.md`. Then write
`.studio/04-BEAT-SHEET.md` defining section-by-section **spatial rhythm**:

- Alternate section archetypes so **no two adjacent sections repeat a
  3-column card row**. The canonical cadence is contained, full-bleed,
  asymmetric split, sticky stage, dense editorial.
- For every section record: name, archetype, grid columns, content density,
  focal point, and scroll intent.
- If `MOTION_INTENSITY >= 5` or the page uses scrollytelling at all, include
  the **Scrollytelling Beat Table** mapping every `data-step` ID to its card
  copy (40 words maximum per card), its `data-camera` target ID, its
  comma-separated `data-layer` IDs, and a `0..1` scrub action.

The IDs you write here become hard contracts. Stage 5 must implement them
exactly or the gate fails.

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase 4 --dir .studio
```

### Stage 5: Senior Frontend Engineer (Full-Output Production Build)

Read `references/spoke-04-implementation-craft.md`. Then implement the complete
interface:

- Consume `.studio/03-TOKENS.css` (link it, import it, or inline it into the
  `@theme`) and match `.studio/04-BEAT-SHEET.md` section for section.
- **Zero truncation**: no `TODO:`, `FIXME:`, `Lorem ipsum`, `// ...` stubs,
  no `Acme Corp`. Write real domain copy at real length.
- Complete interactive states on everything clickable: `:hover`,
  `:focus-visible`, `:active`, plus empty, loading, and error states.
- Ship `@media (prefers-reduced-motion: reduce)` with instant cuts or opacity
  only fallbacks.
- Guarantee 1-to-1 ID matching: every card's `data-camera` and every
  comma-separated `data-layer` value must exist as an `id` in the DOM or SVG
  stage. Typos are loud failures, never silent no-ops.
- Prevent horizontal overflow (`overflow-x: clip`, `text-wrap: balance` on
  headings, `text-wrap: pretty` on body, touch targets at least 44x44px).

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase 5 --dir .studio --target <entry-file-or-src-dir>
```

### Stage 6: QA & Blind Creative Critic (The Gauntlet Loop)

Read `references/spoke-05-gauntlet-verification.md`. Then run the gauntlet for
real:

1. Run the browser inspector at Desktop `1440x900` and Mobile `390x844`:

   ```bash
   node <skill-dir>/scripts/playwright_gauntlet.js --url <url-or-file> --out .studio/screenshots
   ```

2. Require 0 console errors, 0 page errors, 0 broken images, 0 horizontal
   overflow (`scrollWidth <= innerWidth`), and 100 percent `[data-step]`
   activation on scroll.

3. Execute the **Blind Comparison**: strip the labels, put your render next to
   the Stage 2 Reference Bar, and score the four critic axes (hero focal point,
   section rhythm variance, typographic tension, Coco Chanel polish rule).

4. Perform at least **one mandatory polish pass** that removes unnecessary
   decorative chrome or fixes a concrete alignment or spacing tension defect.

5. Write `.studio/06-GAUNTLET-REPORT.md` with screenshots, error counts,
   overflow results, step activation, the reference comparison, the round-by-
   round fixes, and a final `WIN` verdict.

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase 6 --dir .studio --target <entry-file-or-src-dir>
```

## 4. Stage Unlock Table

| Phase | Artifact | Extra input | Gate invocation |
| --- | --- | --- | --- |
| 1 | `.studio/01-BRIEF.md` | none | `--phase 1 --dir .studio` |
| 2 | `.studio/02-MOODBOARD.md` | spoke 1 | `--phase 2 --dir .studio` |
| 3 | `.studio/03-TOKENS.css` | spoke 2 | `--phase 3 --dir .studio` |
| 4 | `.studio/04-BEAT-SHEET.md` | spoke 3 | `--phase 4 --dir .studio` |
| 5 | built UI source | spoke 4 | `--phase 5 --dir .studio --target <src>` |
| 6 | `.studio/06-GAUNTLET-REPORT.md` | spoke 5 | `--phase 6 --dir .studio --target <src>` |

## 5. Failure Playbook

| Symptom | Root cause | Fix |
| --- | --- | --- |
| Gate 3 rejects your CSS | hardcoded AI hex or missing `clamp()` | move to `oklch()` tokens derived from `--brand-hue` |
| Gate 5 reports orphaned IDs | `data-camera` / `data-layer` typo | fix the card or add the missing `id` to the stage |
| Gate 5 finds `TODO:` | you shipped a stub | write the real content now |
| Gate 5 cannot find `prefers-reduced-motion` | no reduced-motion block | add the media query with instant-cut fallbacks |
| Overflow at 390px | fixed width or long unbreakable string | `overflow-x: clip`, `min-width: 0`, wrap the string |
| Step never activates | the card never crosses the IO band, or a competing rAF loop | one move at a time, start from current coordinates |

## 6. Output Contract

At the end of every stage, report:

- The artifact path you wrote.
- The exact command you ran.
- The exact gate line it printed.
- The next stage and the single spoke you will read next.

Never batch six stages into one paragraph. Never skip the quote.
