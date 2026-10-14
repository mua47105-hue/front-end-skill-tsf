# AGENTS.md

Repository instructions for **OpenCode** and every universal `.agents` harness
(Cursor, Codex, Aider, and friends). This repository dogfoods its own skill:
the rules below are the meta-rules, and the skill is the production engine.

## 1. Routing rule (mandatory)

If the task is **any** of the following, you MUST load
`skills/frontend-studio-gauntlet/SKILL.md` and run its 6-stage gauntlet:

- Designing or building a web page, site, landing page, marketing site, or app screen.
- Producing or redesigning UI/UX, a component library surface, or a design system.
- Writing scrollytelling, data-storytelling, or scroll-driven animation.
- Reviewing existing frontend code for "generic", "AI-looking", or "slop" output.
- Producing HTML, CSS, JS/TS, JSX/TSX, Vue, or Svelte that renders a user-facing surface.

Read the hub file first, then read **only** the single
`references/spoke-0N-*.md` assigned to the stage you are currently executing.
Never load all five spokes at once. That is the progressive disclosure contract
that keeps this skill from rotting your context.

## 2. Gate discipline (mandatory)

Every stage writes its artifact into `.studio/` in the target workspace and must
pass the deterministic validator before the next stage unlocks:

```bash
python3 skills/frontend-studio-gauntlet/scripts/verify_gate.py --phase 1 --dir .studio
python3 skills/frontend-studio-gauntlet/scripts/verify_gate.py --phase 2 --dir .studio
python3 skills/frontend-studio-gauntlet/scripts/verify_gate.py --phase 3 --dir .studio
python3 skills/frontend-studio-gauntlet/scripts/verify_gate.py --phase 4 --dir .studio
python3 skills/frontend-studio-gauntlet/scripts/verify_gate.py --phase 5 --dir .studio --target index.html
python3 skills/frontend-studio-gauntlet/scripts/verify_gate.py --phase 6 --dir .studio --target index.html
```

The validator is cumulative: `--phase N` re-verifies phases `1..N-1` first.

Completion is a **verified finding, never a claim**. You are not finished
until `GATE 6 PASSED: ALL FRONTEND STUDIO CRITERIA VERIFIED` is printed by the
Phase 6 run. Never report "done" before that line appears.

## 3. Non-negotiable output rules

- Zero truncation: no `TODO:`, `FIXME:`, `Lorem ipsum`, `// ...`, `<!-- ... -->` stubs.
- Realistic domain copy. Never `Acme Corp`, never `Your text here`.
- Every interactive element has `:hover`, `:focus-visible`, `:active`, plus
  empty and loading states.
- `@media (prefers-reduced-motion: reduce)` is mandatory on motion work.
- No horizontal overflow: `scrollWidth <= innerWidth` at 1440px and 390px.
- Tokens live in `oklch()`; typography uses fluid `clamp()`; spacing is on a
  4px/8px grid.
- Consult `references/spoke-02-tokens-antislop.md` before writing a single
  color or font-family. The AI-slop ban list is enforced by the gate.

## 4. Working in this repository

- Canonical skill source lives in `skills/frontend-studio-gauntlet/`. Never
  edit the harness mirrors; they are generated.
- After changing the skill, regenerate the mirrors:

  ```bash
  bash scripts/sync_harnesses.sh
  bash scripts/sync_harnesses.sh --check   # confirm zero drift
  ```

- Run the full test suite before handing off work:

  ```bash
  python3 -m unittest discover -s tests -p "test_*.py" -v
  ```

- `.studio/`, `screenshots/`, `node_modules/`, and `__pycache__/` are ignored by
  git. Never force-add them.

## 5. Language and runtime constraints

- `scripts/verify_gate.py` uses the **Python 3 standard library only**. Do not
  add third-party imports.
- `scripts/playwright_gauntlet.mjs` uses Playwright if installed and degrades
  gracefully with actionable install instructions if it is not.
