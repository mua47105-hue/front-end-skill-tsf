#!/usr/bin/env python3
"""Deterministic gate validator for the frontend-studio-gauntlet skill.

Six cumulative phases. Each phase writes a required artifact into the target
project's ``.studio/`` directory and must pass this validator before the next
stage unlocks. Running ``--phase N`` always re-verifies phases ``1..N-1`` first,
so a single Phase 6 run re-proves the entire chain end to end.

Completion is a verified finding, never a claim. Phase 6 prints::

    GATE 6 PASSED: ALL FRONTEND STUDIO CRITERIA VERIFIED

Standard library only: argparse, pathlib, re, sys.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TOOL_NAME = "frontend-studio-gauntlet"

GATE_MESSAGES = {
    1: "BRIEF AND TASTE DIALS VERIFIED",
    2: "NAMED QUALITY BAR VERIFIED",
    3: "OKLCH TOKEN SYSTEM VERIFIED",
    4: "RHYTHM AND BEAT SHEET VERIFIED",
    5: "FULL-OUTPUT IMPLEMENTATION VERIFIED",
    6: "ALL FRONTEND STUDIO CRITERIA VERIFIED",
}

# --------------------------------------------------------------------------
# Shared rules
# --------------------------------------------------------------------------

#: Banned truncation stubs. Matching any of these fails the owning phase.
#: Written with \s+ escapes so this validator never stores the raw forbidden
#: strings that it is supposed to detect.
PLACEHOLDER_PATTERNS = (
    ("TODO:", re.compile(r"TODO:")),
    ("FIXME:", re.compile(r"FIXME:")),
    ("Lorem ipsum", re.compile(r"Lorem\s+ipsum", re.IGNORECASE)),
    ("... rest of", re.compile(r"\.\.\.\s*rest\s+of", re.IGNORECASE)),
    ("// ...", re.compile(r"//\s*\.\.\.")),
    ("<!-- ... -->", re.compile(r"<!--\s*\.\.\.")),
    ("Acme-Corp", re.compile(r"\bAcme\s+Corp\b", re.IGNORECASE)),
    ("Lorem-Inc", re.compile(r"\bLorem\s+Inc\b", re.IGNORECASE)),
    ("Your-text-here", re.compile(r"Your\s+text\s+here", re.IGNORECASE)),
    (
        "<template-placeholder>",
        re.compile(
            r"<(?:one line[^>\n]*|specific title[^>\n]*|working-url[^>\n]*|"
            r"concrete defect|specific change|chanel subtraction[^>\n]*|"
            r"chandel subtraction[^>\n]*|WIN\s*\|\s*BLOCKED|1-10)>",
            re.IGNORECASE,
        ),
    ),
)

#: Default AI palette tells. Never allowed in the token system.
#: The last three are the indigo/purple gradient defaults; the terracotta is
#: the assistant-default warm accent.
BANNED_HEX = ("#6366f1", "#a855f7", "#8b5cf6", "#d97757")

#: File types the Stage 5 implementation scan inspects.
SOURCE_SUFFIXES = frozenset(
    {
        ".html",
        ".htm",
        ".jsx",
        ".tsx",
        ".vue",
        ".svelte",
        ".css",
        ".js",
        ".mjs",
        ".cjs",
        ".ts",
    }
)

#: Directories that never contain hand-written page source.
SKIP_DIRS = frozenset(
    {
        "node_modules",
        ".git",
        ".next",
        ".nuxt",
        ".svelte-kit",
        ".turbo",
        ".output",
        "dist",
        "build",
        "out",
        "coverage",
        "vendor",
        "__pycache__",
        ".studio",
        ".cache",
    }
)

URL_RE = re.compile(r"https?://[^\s)\]\}\"'<>]+")
INTEGER_RE = re.compile(r"(?<!\d)(\d{1,3})(?!\d)")

#: Scrollytelling ids and attributes must be findable in plain HTML *and* in
#: JSX/TSX, where values are string expressions: id="x", id={"x"}, id={`x`},
#: or bound from a step object literal such as { id: "step-01", camera:
#: "cam-establish", layers: ["edge-network"] }.
ID_ATTR_RE = re.compile(
    r"""\bid\s*=\s*(?:["']([^"']+)["']|\{\s*["'`]([^"'`]+)["'`]\s*\})"""
)
ID_PROP_RE = re.compile(r"""\bid\s*:\s*["'`]([A-Za-z0-9_-]+)["'`]""")

DATA_CAMERA_RE = re.compile(
    r"""\bdata-camera\s*=\s*(?:["']([^"']+)["']|\{\s*["'`]([^"'`]+)["'`]\s*\})"""
)
DATA_LAYER_RE = re.compile(
    r"""\bdata-layer\s*=\s*(?:["']([^"']+)["']|\{\s*["'`]([^"'`]+)["'`]\s*\})"""
)
STEP_CAMERA_PROP_RE = re.compile(r"""\bcamera\s*:\s*["'`]([A-Za-z0-9_-]+)["'`]""")
STEP_LAYERS_PROP_RE = re.compile(r"""\blayers\s*:\s*\[([^\]]+)\]""")
STRING_LITERAL_RE = re.compile(r"""["'`]([A-Za-z0-9_-]+)["'`]""")

#: Design Spell markers, e.g. data-spell="magnetic-spring".
SPELL_ATTR_RE = re.compile(
    r"""\bdata-spell\s*=\s*(?:["']([^"']+)["']|\{\s*["'`]([^"'`]+)["'`]\s*\})"""
)

#: Characters that mark a JSX expression as dynamic rather than a literal id.
DYNAMIC_EXPR_CHARS = (".", "(", ")", "[", "]", "$", " ")


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------


class PhaseReport:
    """Collects the checked lines and failures for exactly one phase."""

    def __init__(self, phase: int) -> None:
        self.phase = phase
        self.failures: list[str] = []
        self.notes: list[str] = []

    def ok(self, message: str) -> None:
        self.notes.append(message)

    def fail(self, message: str) -> None:
        self.failures.append(message)

    @property
    def passed(self) -> bool:
        return not self.failures

    def render(self) -> None:
        print(f"  [phase {self.phase}]")
        for note in self.notes:
            print(f"    ok   {note}")
        for failure in self.failures:
            print(f"    FAIL {failure}")


def read_text(path: Path) -> str:
    """Read a file as text without ever raising on odd bytes."""
    return path.read_text(encoding="utf-8", errors="replace")


def check_placeholders(text: str, label: str, report: PhaseReport) -> None:
    """Fail the report on any banned truncation stub inside ``text``."""
    for name, pattern in PLACEHOLDER_PATTERNS:
        match = pattern.search(text)
        if match:
            line_no = text.count("\n", 0, match.start()) + 1
            report.fail(
                f"{label}:{line_no}: banned placeholder or truncation stub "
                f"detected ({name}). Write the real content instead."
            )


def require_file(
    path: Path, min_chars: int, report: PhaseReport, description: str
) -> str | None:
    """Load a required artifact and enforce its minimum size."""
    if not path.exists():
        report.fail(f"required artifact missing: {path}")
        return None
    if not path.is_file():
        report.fail(f"required artifact is not a file: {path}")
        return None
    text = read_text(path)
    if len(text.strip()) < min_chars:
        report.fail(
            f"{path.name} is too thin ({len(text.strip())} chars, "
            f"minimum {min_chars}). {description}"
        )
        return None
    report.ok(f"{path.name} present ({len(text.strip())} chars >= {min_chars})")
    return text


def require_headings(text: str, headings, path_name: str, report: PhaseReport) -> None:
    """Every required heading must appear verbatim."""
    missing = [heading for heading in headings if heading not in text]
    if missing:
        for heading in missing:
            report.fail(f"{path_name} is missing required heading '{heading}'")
    else:
        report.ok(f"{path_name} declares all {len(headings)} required headings")


# --------------------------------------------------------------------------
# Phase 1: Product Director
# --------------------------------------------------------------------------

BRIEF_HEADINGS = (
    "Aesthetic Archetype",
    "Divergent Metaphor Exploration",
    "Hero Interactive Instrument",
)
DIALS = ("DESIGN_VARIANCE", "MOTION_INTENSITY", "VISUAL_DENSITY")

#: All three divergent-metaphor steps must be documented, not just the winner.
METAPHOR_STEPS = (
    "Rejected Industry Cliche",
    "Rejected Safe Editorial",
    "Selected Lateral World Metaphor",
)


def find_dial(text: str, dial: str) -> int | None:
    """Return the first integer stated for ``dial``, or None when unstated.

    Preference order: a number after the dial name on the same line, then any
    number on that line, then any number on one of the next three lines. That
    covers ``DESIGN_VARIANCE: 7``, a markdown table cell, and a dial written
    as a heading followed by its rating.
    """
    lines = text.splitlines()
    for index, line in enumerate(lines):
        position = line.find(dial)
        if position < 0:
            continue
        tail = INTEGER_RE.search(line[position:])
        if tail:
            return int(tail.group(1))
        head = INTEGER_RE.search(line)
        if head:
            return int(head.group(1))
        for probe in lines[index + 1 : index + 4]:
            found = INTEGER_RE.search(probe)
            if found:
                return int(found.group(1))
    return None


def verify_phase_1(studio: Path, report: PhaseReport) -> None:
    path = studio / "01-BRIEF.md"
    text = require_file(
        path, 200, report, "The brief must name audience, job-to-be-done, and dials."
    )
    if text is None:
        return
    require_headings(text, BRIEF_HEADINGS + DIALS, path.name, report)
    for dial in DIALS:
        value = find_dial(text, dial)
        if value is None:
            report.fail(
                f"{path.name} states no explicit integer rating for {dial}; "
                "rate it from 1 to 10"
            )
        elif not 1 <= value <= 10:
            report.fail(
                f"{path.name} rates {dial} as {value}; the taste dials are "
                "integers from 1 to 10"
            )
        else:
            report.ok(f"{dial} = {value}/10")

    missing_steps = [step for step in METAPHOR_STEPS if step not in text]
    if missing_steps:
        for step in missing_steps:
            report.fail(
                f"{path.name} is missing the divergent metaphor step "
                f"'{step}'. Document all three concepts: the rejected industry "
                "cliche, the rejected safe editorial, and the selected lateral "
                "world metaphor."
            )
    else:
        report.ok(
            f"{path.name} documents all {len(METAPHOR_STEPS)} divergent "
            "metaphor steps"
        )

    if re.search(r"data-interactive-hero", text):
        report.ok("hero instrument is marked data-interactive-hero")
    else:
        report.fail(
            f"{path.name} defines a Hero Interactive Instrument but never marks "
            "it data-interactive-hero. Stage 5 must be able to find it."
        )

    check_placeholders(text, path.name, report)


# --------------------------------------------------------------------------
# Phase 2: Visual Researcher
# --------------------------------------------------------------------------

MOODBOARD_HEADINGS = (
    "Primary Bar",
    "Hero Treatment",
    "Grid & Section Rhythm",
    "Typography Behavior",
)


def verify_phase_2(studio: Path, report: PhaseReport) -> None:
    path = studio / "02-MOODBOARD.md"
    text = require_file(
        path,
        300,
        report,
        "A Named, Fetchable, Comparable quality bar needs real detail.",
    )
    if text is None:
        return
    require_headings(text, MOODBOARD_HEADINGS, path.name, report)
    urls = URL_RE.findall(text)
    if not urls:
        report.fail(
            f"{path.name} contains no http:// or https:// reference URL. "
            "A quality bar that cannot be fetched is not a quality bar."
        )
    else:
        unique = sorted(set(urls))
        report.ok(f"{len(unique)} fetchable reference URL(s), e.g. {unique[0]}")
    check_placeholders(text, path.name, report)


# --------------------------------------------------------------------------
# Phase 3: Design Systems Architect
# --------------------------------------------------------------------------

TOKEN_REQUIREMENTS = (
    (":root", "a :root token block"),
    ("oklch(", "perceptual oklch() color values"),
    ("clamp(", "fluid clamp() typography sizes"),
    ("--font-", "at least one --font- family token"),
)


def verify_phase_3(studio: Path, report: PhaseReport) -> None:
    path = studio / "03-TOKENS.css"
    text = require_file(
        path,
        250,
        report,
        "The token system must be a pasteable stylesheet, not a mood swatch.",
    )
    if text is None:
        return
    for token, description in TOKEN_REQUIREMENTS:
        if token in text:
            report.ok(f"03-TOKENS.css declares {description}")
        else:
            report.fail(f"03-TOKENS.css must declare {description} ('{token}')")

    lowered = text.lower()
    hits = [hex_code for hex_code in BANNED_HEX if hex_code in lowered]
    if hits:
        report.fail(
            "03-TOKENS.css uses banned AI-default hex code(s): "
            + ", ".join(hits)
            + ". Derive colors from --brand-hue and --accent-hue with oklch() "
            "instead of shipping the default AI palette."
        )
    else:
        report.ok(
            "no banned AI-default hex codes ("
            + ", ".join(BANNED_HEX)
            + ")"
        )

    hue_seed = "--brand-hue" in text and "--accent-hue" in text
    if hue_seed:
        report.ok("colors are derived from the --brand-hue / --accent-hue seeds")
    else:
        report.fail(
            "03-TOKENS.css must derive its palette from --brand-hue and "
            "--accent-hue rather than fixed color literals"
        )
    check_placeholders(text, path.name, report)


# --------------------------------------------------------------------------
# Phase 4: Principal UX & Motion Architect
# --------------------------------------------------------------------------

BEAT_SHEET_HEADINGS = (
    "Page Rhythm Overview",
    "Hero Interactive Instrument",
    "Design Spells",
)


def verify_phase_4(studio: Path, report: PhaseReport) -> None:
    path = studio / "04-BEAT-SHEET.md"
    text = require_file(
        path,
        250,
        report,
        "The beat sheet must define section rhythm section by section.",
    )
    if text is None:
        return
    require_headings(text, BEAT_SHEET_HEADINGS, path.name, report)

    steps = set(re.findall(r"\bdata-step\b|\bstep-\d{2}\b", text))
    if steps:
        report.ok(f"{len(steps)} scrollytelling step(s) declared in the beat sheet")
        table_row = re.search(r"data-camera", text)
        if table_row:
            report.ok("scrollytelling beat table maps steps to data-camera targets")
        else:
            report.fail(
                f"{path.name} declares scrollytelling steps but has no beat table "
                "column mapping them to data-camera targets"
            )
    else:
        # A high MOTION_INTENSITY dial makes the beat table mandatory, so a
        # sheet that silently drops scrollytelling fails instead of passing.
        brief_path = studio / "01-BRIEF.md"
        motion_dial = None
        if brief_path.is_file():
            motion_dial = find_dial(read_text(brief_path), "MOTION_INTENSITY")
        if motion_dial is not None and motion_dial >= 5:
            report.fail(
                f"{path.name} declares no scrollytelling steps, but 01-BRIEF.md "
                f"sets MOTION_INTENSITY: {motion_dial}. At 5 or above the "
                "Scrollytelling Beat Table is mandatory: add the data-step, "
                "data-camera, and data-layer mapping, or lower the dial."
            )
        else:
            observed = (
                f"MOTION_INTENSITY from 01-BRIEF.md is {motion_dial}"
                if motion_dial is not None
                else "MOTION_INTENSITY was not stated in 01-BRIEF.md"
            )
            report.ok(
                "no scrollytelling declared; "
                f"{observed}, which is below the 5 threshold where the beat "
                "table becomes mandatory"
            )
    check_placeholders(text, path.name, report)


# --------------------------------------------------------------------------
# Phase 5: Senior Frontend Engineer
# --------------------------------------------------------------------------


def clean_attr_value(raw: str) -> str:
    """Normalize a JSX or template-literal attribute value to a bare id.

    Returns ``""`` when the value is a dynamic JS expression rather than a
    literal id, so ``data-camera={step.camera}`` is skipped instead of being
    mis-read as the literal string ``step.camera``.
    """
    value = raw.strip()
    value = value.strip("`").strip()
    while value.startswith("{") and value.endswith("}"):
        value = value[1:-1].strip()
    value = value.strip("`").strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    value = value.strip()
    if any(char in value for char in DYNAMIC_EXPR_CHARS):
        return ""
    return value


def extract_defined_ids(combined: str) -> set[str]:
    """Every id defined in the target: HTML/JSX attributes plus object literals."""
    ids: set[str] = set()
    for match in ID_ATTR_RE.finditer(combined):
        value = clean_attr_value(match.group(1) or match.group(2) or "")
        if value:
            ids.add(value)
    for match in ID_PROP_RE.finditer(combined):
        value = clean_attr_value(match.group(1))
        if value:
            ids.add(value)
    return ids


def extract_scrolly_references(combined: str) -> list[str]:
    """Every data-camera / data-layer target referenced by a scroll step.

    Static HTML attributes and JSX string literals are always collected. Step
    object literals (``camera: "cam-x"`` / ``layers: ["a", "b"]``) are only
    collected when the file actually opts into scrollytelling via a
    ``data-step`` / ``data-camera`` / ``data-layer`` marker, so unrelated
    ``camera:`` keys in unrelated code are never mistaken for targets.
    """
    references: list[str] = []

    def add(value: str) -> None:
        cleaned = clean_attr_value(value)
        if cleaned and cleaned not in references:
            references.append(cleaned)

    for match in DATA_CAMERA_RE.finditer(combined):
        add(match.group(1) or match.group(2) or "")
    for match in DATA_LAYER_RE.finditer(combined):
        raw = match.group(1) or match.group(2) or ""
        for part in raw.split(","):
            add(part)

    uses_scrolly = any(
        marker in combined
        for marker in ("data-step", "data-camera", "data-layer")
    )
    if uses_scrolly:
        for match in STEP_CAMERA_PROP_RE.finditer(combined):
            add(match.group(1))
        for match in STEP_LAYERS_PROP_RE.finditer(combined):
            for literal in STRING_LITERAL_RE.findall(match.group(1)):
                add(literal)

    return references


def collect_sources(target: Path) -> list[Path]:
    """Every hand-written source file under ``target``, deterministically sorted."""
    if target.is_file():
        return [target] if target.suffix.lower() in SOURCE_SUFFIXES else []
    if not target.is_dir():
        return []
    found: list[Path] = []
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        found.append(path)
    return found


def verify_phase_5(studio: Path, target: Path | None, report: PhaseReport) -> None:
    if target is None:
        report.fail(
            "Phase 5 requires --target <entry-file-or-src-dir> so the "
            "implementation can be scanned for placeholders and orphaned ids"
        )
        return

    files = collect_sources(target)
    if not files:
        report.fail(
            f"no source files found under target '{target}'. Point --target at "
            "the entry file or the source directory (html, css, js, ts, jsx, "
            "tsx, vue, svelte)."
        )
        return
    report.ok(f"scanning {len(files)} source file(s) under '{target}'")

    chunks: list[str] = []
    for path in files:
        text = read_text(path)
        chunks.append(text)
        check_placeholders(text, path.name, report)

    combined = "\n".join(chunks)

    # A high DESIGN_VARIANCE dial is a promise that the page ships an
    # instrument and named tactile interactions, not a static render.
    brief_path = studio / "01-BRIEF.md"
    variance_dial = None
    if brief_path.is_file():
        variance_dial = find_dial(read_text(brief_path), "DESIGN_VARIANCE")

    if variance_dial is not None and variance_dial >= 6:
        if "data-interactive-hero" in combined:
            hero_hits = len(re.findall(r"data-interactive-hero", combined))
            report.ok(
                f"DESIGN_VARIANCE {variance_dial}: data-interactive-hero "
                f"present ({hero_hits} occurrence(s))"
            )
        else:
            report.fail(
                f"DESIGN_VARIANCE is {variance_dial}, so the hero centerpiece "
                "must be an interactive instrument. No data-interactive-hero "
                "attribute was found under the target. Add it to the hero "
                "markup, or lower DESIGN_VARIANCE to 5 or below."
            )

        spell_names = sorted(
            {
                cleaned
                for match in SPELL_ATTR_RE.findall(combined)
                for cleaned in (clean_attr_value(match[0] or match[1] or ""),)
                if cleaned
            }
        )
        spell_count = len(spell_names)
        if spell_count >= 2:
            report.ok(
                f"DESIGN_VARIANCE {variance_dial}: {spell_count} distinct "
                f"Design Spell(s) declared: {', '.join(spell_names)}"
            )
        else:
            occurrences = len(re.findall(r"\bdata-spell\b", combined))
            detail = (
                f"only {spell_count} distinct spell name(s)"
                if occurrences
                else "no data-spell attribute at all"
            )
            report.fail(
                f"DESIGN_VARIANCE is {variance_dial}, so at least 2 "
                f"data-spell=\"...\" elements are required, but found {detail}. "
                "Ship at least two named tactile micro-interactions, or lower "
                "DESIGN_VARIANCE to 5 or below."
            )
    elif variance_dial is not None:
        report.ok(
            f"DESIGN_VARIANCE {variance_dial} is below the interactive-hero "
            "threshold of 6, so the instrument and spell checks are skipped"
        )

    if "prefers-reduced-motion" in combined:
        report.ok("prefers-reduced-motion handling present in source")
    else:
        report.fail(
            "no prefers-reduced-motion media query found under the target. "
            "Motion work must ship a reduced-motion fallback."
        )

    defined_ids = extract_defined_ids(combined)
    referenced = extract_scrolly_references(combined)

    if not referenced:
        report.ok("no data-camera / data-layer references to reconcile")
        return

    missing = [name for name in referenced if name not in defined_ids]
    if missing:
        report.fail(
            "orphaned scrollytelling targets: "
            + ", ".join(missing)
            + ". Every data-camera and comma-separated data-layer value must "
            "exist as an id in the DOM or SVG stage."
        )
    else:
        report.ok(
            f"all {len(referenced)} data-camera / data-layer target(s) resolve "
            f"to real ids ({len(defined_ids)} id attribute(s) parsed)"
        )


# --------------------------------------------------------------------------
# Phase 6: QA & Blind Creative Critic
# --------------------------------------------------------------------------

REPORT_HEADINGS = (
    "Desktop Screenshot",
    "Mobile Screenshot",
    "Console / Page Errors",
    "Horizontal Overflow Check",
    "Reference Bar Compared",
    "Round 1 Critic Findings & Fixes Applied",
    "Final Verdict",
)

CONSOLE_ERROR_COUNT_RE = re.compile(r"console\.error\s+count\s*:\s*(\d+)", re.IGNORECASE)
PAGE_ERROR_COUNT_RE = re.compile(r"pageerror\s+count\s*:\s*(\d+)", re.IGNORECASE)
TEMPLATE_VERDICT_RE = re.compile(r"<\s*WIN\s*\|\s*BLOCKED\s*>", re.IGNORECASE)
BLOCKED_VERDICT_RE = re.compile(r"Verdict\s*:\s*BLOCKED", re.IGNORECASE)


def verify_phase_6(studio: Path, target: Path | None, report: PhaseReport) -> None:
    if target is None:
        report.fail(
            "Phase 6 requires --target <entry-file-or-src-dir> so the verified "
            "build is re-proven while the gauntlet report is graded"
        )
        return

    path = studio / "06-GAUNTLET-REPORT.md"
    text = require_file(
        path,
        250,
        report,
        "The gauntlet report must carry screenshots, machine checks, the blind "
        "comparison, and the round-by-round fixes.",
    )
    if text is None:
        return
    require_headings(text, REPORT_HEADINGS, path.name, report)
    check_placeholders(text, path.name, report)

    # A machine pass that reported errors is not a WIN. Both counts must be 0.
    for label, pattern in (
        ("console.error count", CONSOLE_ERROR_COUNT_RE),
        ("pageerror count", PAGE_ERROR_COUNT_RE),
    ):
        match = pattern.search(text)
        if match is None:
            report.ok(f"{label} not stated in the report")
        elif int(match.group(1)) > 0:
            report.fail(
                f"{path.name} reports {label}: {match.group(1)}. The gauntlet "
                "must show 0 console errors and 0 page errors before a WIN is "
                "recorded. Fix them, re-run, and re-capture."
            )
        else:
            report.ok(f"{label}: {match.group(1)}")

    marker = text.find("Final Verdict")
    verdict = text[marker:] if marker >= 0 else text

    if TEMPLATE_VERDICT_RE.search(verdict):
        report.fail(
            f"{path.name} still contains the unedited template verdict "
            "'<WIN | BLOCKED>'. Replace it with the real verdict you observed."
        )
    elif BLOCKED_VERDICT_RE.search(verdict):
        report.fail(
            f"{path.name} records a BLOCKED verdict. A blocked browser run is "
            "never a WIN: install Playwright, run the gauntlet for real, then "
            "rewrite the verdict."
        )
    elif re.search(r"\bWIN\b", verdict):
        report.ok("final verdict records a WIN")
    else:
        report.fail(
            f"{path.name} does not record a WIN in the Final Verdict section. "
            "Run the blind comparison and the mandatory refinement pass, or "
            "record BLOCKED with the reason."
        )


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------


def verify_phase(phase: int, studio: Path, target: Path | None) -> PhaseReport:
    report = PhaseReport(phase)
    if phase == 1:
        verify_phase_1(studio, report)
    elif phase == 2:
        verify_phase_2(studio, report)
    elif phase == 3:
        verify_phase_3(studio, report)
    elif phase == 4:
        verify_phase_4(studio, report)
    elif phase == 5:
        verify_phase_5(studio, target, report)
    elif phase == 6:
        verify_phase_6(studio, target, report)
    else:  # pragma: no cover - argparse restricts the range
        report.fail(f"unknown phase {phase}")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="verify_gate.py",
        description=(
            f"Deterministic gate validator for the {TOOL_NAME} skill. "
            "Verifies stages 1..N cumulatively."
        ),
    )
    parser.add_argument(
        "--phase",
        type=int,
        required=True,
        choices=[1, 2, 3, 4, 5, 6],
        help="highest stage to verify; stages 1..N-1 are re-verified first",
    )
    parser.add_argument(
        "--dir",
        default=".studio",
        help="directory holding the 01..06 artifacts (default: .studio)",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="entry file or source directory to scan (required for phases 5 and 6)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    studio = Path(args.dir).expanduser()
    target = Path(args.target).expanduser() if args.target else None

    if not studio.is_dir():
        print(
            f"GATE {args.phase} FAILED: studio directory not found: {studio}\n"
            "create it and write the stage artifacts before running the gate.",
            file=sys.stderr,
        )
        return 1

    print(f"{TOOL_NAME} gate run")
    print(f"  studio directory : {studio}")
    print(f"  target           : {target if target else '(none)'}")
    print(f"  verifying phases : 1..{args.phase} (cumulative)")
    print("")

    for phase in range(1, args.phase + 1):
        report = verify_phase(phase, studio, target)
        report.render()
        if not report.passed:
            print("")
            print(f"GATE {phase} FAILED: {len(report.failures)} blocking issue(s)")
            for failure in report.failures:
                print(f"  - {failure}")
            print("")
            print(
                f"Fix the Stage {phase} artifact or implementation, then re-run "
                f"--phase {phase}."
            )
            return 1
        print(f"GATE {phase} PASSED: {GATE_MESSAGES[phase]}")
        print("")

    if args.phase == 6:
        print(
            "Completion is a verified finding: Stage 2 bar, Stage 4 rhythm, "
            "Stage 5 implementation, and the Stage 6 blind comparison are all "
            "on disk and re-proven by this run."
        )
    else:
        print(f"Stage {args.phase} is verified. Stage {args.phase + 1} is now unlocked.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
