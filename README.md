# frontend-studio-gauntlet

A production, open-source **AI Agent Skill** that turns "build me a landing
page" into a six-stage design studio with deterministic proof at the end.

The premise: language models do not fail at frontend because they cannot write
CSS. They fail because they produce **generic** output. Every page gets the same
centered hero, the same three rounded cards, the same indigo gradient, and the
same `Inter` at the same size. This skill attacks that failure directly with
process, tokens, mechanical gates, and a blind critique loop.

**Completion is a verified finding, never a claim.** The run is not done until
the validator prints:

```text
GATE 6 PASSED: ALL FRONTEND STUDIO CRITERIA VERIFIED
```

## Contents

- [Architecture](#architecture)
- [The Six Stages](#the-six-stages)
- [The Five Spokes](#the-five-spokes)
- [Install](#install)
- [Usage](#usage)
- [The Gate Validator](#the-gate-validator)
- [The Browser Gauntlet](#the-browser-gauntlet)
- [What It Rejects](#what-it-rejects)
- [Repository Layout](#repository-layout)
- [Testing](#testing)
- [License](#license)

## Architecture

Hub-and-spoke progressive disclosure. The hub stays small enough to never
context-rot; the deep domain rules load one at a time.

```text
                 +--------------------------------------------------+
                 |  AGENTS.md / CLAUDE.md   (harness routing)        |
                 +---------------------------+----------------------+
                                             |
                                             v
 +---------------------------------------  +----------------------------+
 |  .opencode/skills/                      |  skills/                  |
 |  .agents/skills/      <-- synced by --> |  frontend-studio-gauntlet |
 |  .claude/skills/                        |  SKILL.md  (HUB, <260)   |
 +----------------------------------------+ +------------+------------+
                                                          |
     +----------------+----------------+------------------+-----------------+
     |                |                |                  |                 |
     v                v                v                  v                 v
 +----------+  +--------------+  +---------------+  +--------------------+  +-------------------+
 | spoke-01 |  |   spoke-02   |  |    spoke-03   |  |      spoke-04      |  |     spoke-05      |
 | research |  | tokens+ban   |  | rhythm+scroll |  |     engineering    |  |   QA + blind      |
 +----------+  +--------------+  +---------------+  +--------------------+  +-------------------+
     S2             S3                S4                  S5                    S6
                                                         |
                                          +--------------+--------------+
                                          |                             |
                                          v                             v
                                 +------------------+        +---------------------+
                                 | .studio/01..06   |        | playwright_gauntlet |
                                 | artifacts        |        | .mjs (headless)     |
                                 +------------------+        +---------------------+
                                          |
                                          v
                                 +------------------------+
                                 |    verify_gate.py      |
                                 |  deterministic, stdlib |
                                 +------------------------+
```

Every stage writes an artifact into `.studio/` and passes the gate before the
next stage unlocks. The validator is cumulative, so a single Phase 6 run
re-proves Phases 1 through 5.

## The Six Stages

| # | Stage | Artifact | What the gate proves |
| --- | --- | --- | --- |
| 1 | Product Director | `.studio/01-BRIEF.md` | audience, job-to-be-done, Aesthetic Archetype, and three explicit 1-10 dials (`DESIGN_VARIANCE`, `MOTION_INTENSITY`, `VISUAL_DENSITY`) |
| 2 | Visual Researcher | `.studio/02-MOODBOARD.md` | a Named, Fetchable, Comparable bar with real `https://` references and extracted hero, grid, type, and media mechanics |
| 3 | Design Systems Architect | `.studio/03-TOKENS.css` | perceptual `oklch()` colors from `--brand-hue` / `--accent-hue`, fluid `clamp()` type scale, font tokens, zero banned AI hexes |
| 4 | Principal UX & Motion Architect | `.studio/04-BEAT-SHEET.md` | section-by-section rhythm with no adjacent 3-column card rows, plus the scrollytelling beat table when motion is involved |
| 5 | Senior Frontend Engineer | your source tree | zero truncation, `prefers-reduced-motion` present, and every `data-camera` / `data-layer` value resolving to a real `id` |
| 6 | QA & Blind Creative Critic | `.studio/06-GAUNTLET-REPORT.md` | screenshots, 0 console/page errors, 0 overflow, 100% step activation, blind comparison, a real polish pass, and a `WIN` verdict |

## The Five Spokes

| Spoke | File | Owns |
| --- | --- | --- |
| 01 | `references/spoke-01-inspiration.md` | the research bench (Pinterest, Awwwards, Godly, Mobbin, The Pudding, Land-book, Design Spells), archetype search operators, and the 3 rules of a valid quality bar |
| 02 | `references/spoke-02-tokens-antislop.md` | the Anti-Slop Ban List (fonts, AI hexes, layout tells), single-hue OKLCH token math, fluid type scale, spacing grid, easing |
| 03 | `references/spoke-03-scrollytelling-layout.md` | anti-template page rhythm, the 5 canonical scrollytelling mechanics, engineering invariants, and the beat sheet template |
| 04 | `references/spoke-04-implementation-craft.md` | full-output enforcement, a zero-dependency SVG camera controller, a React + Tailwind v4 + GSAP pinned stage, specificity rules, reduced motion |
| 05 | `references/spoke-05-gauntlet-verification.md` | headless runtime verification, the blind comparison protocol, the 4 critic axes, and the gauntlet report template |

The hub instructs the agent to load exactly one spoke per stage. That is the
point: loading all five at once is what causes context rot.

## Install

The skill is plain Markdown plus two scripts. Pick your harness.

### OpenCode

```bash
git clone https://github.com/your-org/frontend-studio-gauntlet.git
cd frontend-studio-gauntlet
bash scripts/sync_harnesses.sh
```

Then, in any project, ask for the skill by name:

```text
Use the frontend-studio-gauntlet skill to build ...
```

Or link it into an existing OpenCode workspace:

```bash
ln -s /path/to/frontend-studio-gauntlet/skills/frontend-studio-gauntlet \
      ~/.config/opencode/skills/frontend-studio-gauntlet
```

### Claude Code

```bash
git clone https://github.com/your-org/frontend-studio-gauntlet.git
cd frontend-studio-gauntlet
bash scripts/sync_harnesses.sh
```

Claude Code reads `.claude/skills/` automatically. Invoke it with:

```text
/frontend-studio-gauntlet build a landing page for a developer observability tool
```

### Cursor

Cursor reads `.agents/skills/` in recent versions. Run the sync script, then
Cursor picks up the skill with no further configuration. For older Cursor
releases, paste `SKILL.md` into `.cursor/rules/frontend-studio-gauntlet.mdc`.

### Codex and universal `.agents` harnesses

Any harness that honors the `.agents/skills/` convention works with the same
one-line sync:

```bash
bash scripts/sync_harnesses.sh
```

### `npx skills add`

```bash
npx skills add frontend-studio-gauntlet
```

Or from a local checkout:

```bash
npx skills add ./skills/frontend-studio-gauntlet
```

### Verify the mirrors

```bash
bash scripts/sync_harnesses.sh --check
```

Exits 0 when every mirror is byte-identical to the canonical source, 1 on drift.

## Usage

### Drive it conversationally

```text
Build a landing page for a company that sells e-bike battery diagnostics.
Use the frontend-studio-gauntlet skill.
```

The agent will:

1. Write `.studio/01-BRIEF.md` and print `GATE 1 PASSED: ...`.
2. Research, write `.studio/02-MOODBOARD.md`, print `GATE 2 PASSED: ...`.
3. Author `.studio/03-TOKENS.css`, print `GATE 3 PASSED: ...`.
4. Write `.studio/04-BEAT-SHEET.md`, print `GATE 4 PASSED: ...`.
5. Build the page, print `GATE 5 PASSED: ...`.
6. Screenshot, blind-critique, polish, and print
   `GATE 6 PASSED: ALL FRONTEND STUDIO CRITERIA VERIFIED`.

### Drive it from the CLI

```bash
# validate artifacts only
python3 skills/frontend-studio-gauntlet/scripts/verify_gate.py --phase 4 --dir .studio

# validate the implementation too
python3 skills/frontend-studio-gauntlet/scripts/verify_gate.py --phase 5 --dir .studio --target ./src

# run the browser gauntlet
npm install -D playwright && npx playwright install chromium
node skills/frontend-studio-gauntlet/scripts/playwright_gauntlet.js \
  --url ./index.html --out .studio/screenshots
```

### What the taste dials change

```text
DESIGN_VARIANCE: 8   -> the agent is told to break the container grid on purpose
MOTION_INTENSITY: 7  -> scrollytelling beat table becomes mandatory
VISUAL_DENSITY: 3    -> fewer, larger blocks with far more air
```

## The Gate Validator

`scripts/verify_gate.py` uses **only the Python standard library**
(`argparse`, `pathlib`, `re`, `sys`).

```text
usage: verify_gate.py [-h] --phase {1,2,3,4,5,6} [--dir .studio] [--target TARGET]
```

- `--phase N` verifies Phases `1..N` cumulatively.
- `--dir` points at the `.studio/` artifact directory (default `.studio`).
- `--target` is the entry file or source directory; required for phases 5 and 6.

Exit codes: `0` all gates passed, `1` a gate failed (the blocking issues are
printed), `2` bad CLI usage.

It fails on:

- A missing or too-thin artifact.
- A missing required heading.
- A taste dial with no explicit 1-10 integer.
- A moodboard with no fetchable URL.
- A token sheet without `:root`, `oklch(`, `clamp(`, or `--font-`.
- The banned AI hexes `#6366f1`, `#a855f7`, `#8b5cf6`.
- Any of `TODO:`, `FIXME:`, `Lorem ipsum`, `... rest of`, `// ...`,
  `<!-- ... -->`.
- Source with no `prefers-reduced-motion` handling.
- An orphaned `data-camera` or `data-layer` id, reported by exact name.

## The Browser Gauntlet

`scripts/playwright_gauntlet.js` runs headless Chromium at Desktop
`1440x900` and Mobile `390x844`, trapping console errors and page errors,
checking `documentElement.scrollWidth <= window.innerWidth`, verifying every
`<img>` decoded, and scrolling each `[data-step]` into view to confirm its
active state updates. It writes `desktop-1440x900.png`, `mobile-390x844.png`,
and `report.json` into `--out`, prints a human summary plus JSON, and exits `1`
on any failure. Without Playwright installed it prints exact install commands
and exits `2`, because **blocked is not won**.

## What It Rejects

The Anti-Slop Ban List, enforced by gates and by the blind critic:

- Default AI palettes: `#6366f1`, `#a855f7`, `#8b5cf6`, purple-indigo
  gradients, sterile `#000000` on `#ffffff`.
- Unquestioned `Inter` / `Roboto` / `Open Sans` / `Arial` with no display
  counterpart.
- Tracked-out ALL-CAPS eyebrow badges above every heading.
- Numbered `01 / 02 / 03` markers on non-sequential content.
- Identical 3-column rounded cards with `rgba(0,0,0,0.1)` shadows, repeated.
- Cards nested inside cards.
- An arrow on every CTA.
- One random italicized or accented word per headline.
- `TODO:`, `Lorem ipsum`, `Acme Corp`, and every lazy truncation stub.

## Repository Layout

```text
.
├── AGENTS.md                                  # root agent instructions (OpenCode, universal)
├── CLAUDE.md                                  # root instructions (Claude Code)
├── README.md
├── .gitignore
├── scripts/
│   └── sync_harnesses.sh                      # mirror the skill into every harness
├── skills/
│   └── frontend-studio-gauntlet/
│       ├── SKILL.md                           # HUB: orchestrator + 6-stage state machine
│       ├── references/
│       │   ├── spoke-01-inspiration.md
│       │   ├── spoke-02-tokens-antislop.md
│       │   ├── spoke-03-scrollytelling-layout.md
│       │   ├── spoke-04-implementation-craft.md
│       │   └── spoke-05-gauntlet-verification.md
│       └── scripts/
│           ├── verify_gate.py                 # deterministic gate validator (stdlib only)
│           └── playwright_gauntlet.js        # headless browser inspector
└── tests/
    └── test_verify_gate.py                    # unittest suite for all six gates
```

The three harness mirrors (`.opencode/`, `.agents/`, `.claude/`) are generated
by `scripts/sync_harnesses.sh` and are gitignored to prevent drift. Run the sync
script after cloning.

## Testing

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

The suite covers:

- All six gates passing on a valid mock studio plus a valid scrollytelling page.
- Cumulative behavior: a broken Phase 1 artifact fails Phases 4, 5, and 6.
- Phase 1 failing on missing or out-of-range dial integers.
- Phase 2 failing when reference URLs are absent.
- Phase 3 failing on `#6366f1` and `#a855f7`.
- Phase 5 failing on `TODO:`, `FIXME:`, `Lorem ipsum`, and comment stubs.
- Phase 5 failing when `data-camera="cam-missing"` has no matching SVG `id`,
  and when it reports every orphan by exact name.
- Phase 5 failing when `prefers-reduced-motion` is omitted.
- Phase 6 failing without a `WIN` verdict and re-verifying the implementation.
- The architecture contract: the hub stays under 260 lines, carries no em or
  en dashes, declares valid frontmatter, and the validator imports nothing
  outside the standard library.

## License

MIT. Use it, fork it, ship it inside your own agent stack.
