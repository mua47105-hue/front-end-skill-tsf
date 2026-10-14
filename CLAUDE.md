# CLAUDE.md

Instructions for **Claude Code** working in this repository.

This repo is the source of truth for the `frontend-studio-gauntlet` skill. The
skill is mirrored into `.claude/skills/frontend-studio-gauntlet/` by
`scripts/sync_harnesses.sh`, so Claude Code auto-loads it for frontend work.

## Skill location

- Canonical source: `skills/frontend-studio-gauntlet/SKILL.md`
- Claude Code copy: `.claude/skills/frontend-studio-gauntlet/SKILL.md`
- Regenerate the copy with `bash scripts/sync_harnesses.sh`

## When the skill fires

Load `skills/frontend-studio-gauntlet/SKILL.md` for any task involving web
design, landing pages, UI/UX redesign, design systems, scrollytelling, or
anti-slop frontend engineering. Invoke it explicitly with:

```
/frontend-studio-gauntlet build a landing page for a developer observability tool
```

## Operating rules

1. Read the hub `SKILL.md`, then read **only** the spoke assigned to the
   current stage. Never read all five `references/spoke-*.md` files at once.
2. Every stage writes an artifact into `.studio/` and passes
   `python3 skills/frontend-studio-gauntlet/scripts/verify_gate.py --phase N --dir .studio`
   (add `--target <entry-file-or-src-dir>` for phases 5 and 6) before the next
   stage begins.
3. Do not claim completion before the validator prints
   `GATE 6 PASSED: ALL FRONTEND STUDIO CRITERIA VERIFIED`.
4. No truncation, no `Lorem ipsum`, no `Acme Corp`, no missing interaction
   states, no missing `prefers-reduced-motion` block.
5. Use the `Skill` tool for anything else in this repo's workflow.

## Repository checks

```bash
bash scripts/sync_harnesses.sh
python3 -m unittest discover -s tests -p "test_*.py" -v
```
