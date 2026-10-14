#!/usr/bin/env python3
"""Unittest suite for the frontend-studio-gauntlet gate validator.

Covers all six phases end to end:

- a fully valid studio directory plus a valid scrollytelling page passes 1..6
- Phase 1 fails when a taste dial has no explicit 1-10 integer
- Phase 2 fails when no fetchable https reference URL is present
- Phase 3 fails on the banned AI hex codes #6366f1 and #a855f7
- Phase 5 fails on TODO: and Lorem ipsum stubs
- Phase 5 fails when data-camera="cam-missing" has no matching SVG id
- Phase 5 fails when prefers-reduced-motion is missing
- Phase 6 fails without a WIN verdict and passes with one
- the hub and spoke progressive disclosure architecture holds

Run with:
    python3 -m unittest discover -s tests -p "test_*.py" -v
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "frontend-studio-gauntlet"
VERIFY_GATE = SKILL_DIR / "scripts" / "verify_gate.py"
HUB_SKILL = SKILL_DIR / "SKILL.md"
SPOKE_DIR = SKILL_DIR / "references"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_harnesses.sh"

PHASE_MESSAGES = {
    1: "GATE 1 PASSED: BRIEF AND TASTE DIALS VERIFIED",
    2: "GATE 2 PASSED: NAMED QUALITY BAR VERIFIED",
    3: "GATE 3 PASSED: OKLCH TOKEN SYSTEM VERIFIED",
    4: "GATE 4 PASSED: RHYTHM AND BEAT SHEET VERIFIED",
    5: "GATE 5 PASSED: FULL-OUTPUT IMPLEMENTATION VERIFIED",
    6: "GATE 6 PASSED: ALL FRONTEND STUDIO CRITERIA VERIFIED",
}

BRIEF_TEMPLATE = """# 01 Brief & Taste Dials

## Product

Meridian is an edge observability console for platform engineers who already
run Kubernetes in production and are drowning in per-region dashboards.

## Target Audience

Staff platform engineers at multi-region SaaS companies, 5 to 10 years in,
comfortable with p50 and p99 latency language, tired of stitching four tools
together to answer one question about a request.

## Core Job-to-Be-Done

When a request crosses our edge, help me see exactly where it stalled without
opening a second dashboard.

## Aesthetic Archetype

Swiss editorial meets dark precision cockpit: a dense instrument surface with
generous typographic hierarchy and a single accent hue reserved for live state.

## Taste Dials

- DESIGN_VARIANCE: 7
- MOTION_INTENSITY: 6
- VISUAL_DENSITY: 7

## Priority Surfaces

1. The pinned topology stage that explains the four-hop request path.
2. The region table where engineers compare p50 across three regions.
3. The latency budget readout that drives the primary conversion action.

## Primary Conversion

Read the latency budget, then start a 14 day trace retention trial.
"""

MOODBOARD_TEMPLATE = """# 02 Moodboard & Named Quality Bar

Project: see where an edge request stalls, without a second dashboard.
Archetype: Swiss editorial meets dark precision cockpit.
Motion Intensity: 6

## Primary Bar

- Name: The Pudding, "How The New York Times visualized a year of news"
- URL: https://pudding.cool/
- Screenshot: .studio/screenshots/ref-primary-1440x900.png
- Why comparable: it pins a stage and drives camera moves from scroll steps
  while keeping the annotation cards in a narrow readable column.
- What we steal: the step column width, the pinned stage height, the mono
  annotation labels, and the way each step swaps exactly one layer set.

## Secondary Bar

- Name: Stripe Sessions, developer landing page hero
- URL: https://stripe.com/sessions
- Screenshot: .studio/screenshots/ref-secondary-1440x900.png
- How it differs from the Primary Bar: colder and denser, with a 7/5 hero
  split instead of a pinned stage.
- What we steal: the 7/5 hero split and the single accent hue used only for
  live state.

## Hero Treatment

- Focal point: the stage frame with one live request trace crossing it.
- Aspect and crop: full-bleed 21:9 on desktop, 4:5 crop on mobile.
- Type over media: headline sits in the copy column, never over the stage.
- Depth cues: hairline border and one soft shadow, no gradients, no glow.

## Grid & Section Rhythm

- Column system: 12 column with 7/5 hero split and 4/8 story split.
- Section cadence: asymmetric hero, pinned stage, dense editorial split,
  interactive canvas, full-bleed resolution.
- Density map: airy hero, low text in the story, dense table, airy CTA.
- Repetition ban: no two adjacent 3 column card rows anywhere in the page.

## Typography Behavior

- Display face: Instrument Serif at 700, tracked -0.02em at hero size.
- Text face: Plus Jakarta Sans at 400 and 600, measure 65ch.
- Scale behavior: fluid clamp between 390px and 1440px, hero 44px to 120px.
- Numerals and mono: JetBrains Mono with tabular figures on every metric.

## Color & Surface Texture

- Surface strategy: tinted near neutral paper, no pure white, no pure black.
- Accent discipline: one cyan accent, used only for live and active state.
- Contrast targets: body at 13.2 to 1, muted text at 5.1 to 1.

## Image & Media Art Direction

- Subject matter: schematic network diagrams, never stock photography.
- Treatment: monochrome line art on tinted surface, one accent for live edges.
- Media mix: inline SVG, a small data table, no decorative imagery.
- Motion in media: camera moves only, no ken burns, no parallax on type.
"""

TOKENS_TEMPLATE = """/* 03 TOKENS - perceptual single-hue OKLCH system */

:root {
  color-scheme: light dark;

  --brand-hue: 24;
  --accent-hue: 196;

  --surface-bg: oklch(0.985 0.004 var(--brand-hue));
  --surface-elevated: oklch(1 0 0);
  --surface-sunken: oklch(0.955 0.008 var(--brand-hue));
  --surface-glass: oklch(1 0 0 / 0.62);
  --surface-border: oklch(0.88 0.010 var(--brand-hue));

  --ink-primary: oklch(0.21 0.018 var(--brand-hue));
  --ink-secondary: oklch(0.44 0.016 var(--brand-hue));
  --ink-muted: oklch(0.58 0.012 var(--brand-hue));
  --ink-accent: oklch(0.58 0.17 var(--accent-hue));
  --accent-wash: oklch(0.95 0.045 var(--accent-hue));

  --font-display: "Instrument Serif", Georgia, serif;
  --font-body: "Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  --text-hero: clamp(2.75rem, 1.10rem + 7.2vw, 7.5rem);
  --text-h1: clamp(2.25rem, 1.35rem + 3.9vw, 4.25rem);
  --text-h2: clamp(1.75rem, 1.25rem + 2.2vw, 2.75rem);
  --text-h3: clamp(1.25rem, 1.05rem + 0.9vw, 1.65rem);
  --text-body: clamp(1rem, 0.94rem + 0.28vw, 1.125rem);
  --text-mono: clamp(0.8125rem, 0.78rem + 0.16vw, 0.9rem);

  --space-4: 1rem;
  --space-5: 1.5rem;
  --space-6: 2rem;
  --space-7: 3rem;
  --space-8: 4rem;

  --radius-md: 10px;
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-snap: cubic-bezier(0.16, 1, 0.3, 1);
  --dur-control: 200ms;
  --dur-camera: 900ms;
}

@media (prefers-color-scheme: dark) {
  :root {
    --surface-bg: oklch(0.17 0.012 var(--brand-hue));
    --surface-elevated: oklch(0.21 0.014 var(--brand-hue));
    --ink-primary: oklch(0.96 0.006 var(--brand-hue));
    --ink-secondary: oklch(0.78 0.012 var(--brand-hue));
    --ink-accent: oklch(0.74 0.15 var(--accent-hue));
  }
}
"""

BEAT_SHEET_TEMPLATE = """# 04 Beat Sheet - Wireframe & Scroll Choreography

Project: the four-hop edge request story for platform engineers.
DESIGN_VARIANCE: 7   MOTION_INTENSITY: 6   VISUAL_DENSITY: 7
Mechanic chosen: Pan-and-Zoom Camera Stage

## Page Rhythm Overview

| # | Section | Archetype | Density | Grid | Focal point | Scroll intent |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Hero | Asymmetric 7/5 split | medium | 12-col, copy 7 / meta 5 | the live trace | introduce the promise |
| 2 | How it works | Sticky stage | low text | 12-col, steps 4 / stage 8 | pinned SVG | pin and scrub |
| 3 | Regions | Editorial split 5/7 | high | 12-col, prose 5 / table 7 | the metric row | slow read |
| 4 | Budget | Interactive canvas | medium | full-bleed | the live control | hands on |
| 5 | Resolution | Full-bleed CTA | very low | single center | the one button | convert |

Repetition ban: no two adjacent sections share a layout archetype, and no two
adjacent sections may both be 3 column card rows. Section 2 is the only pinned
section and the only section with scroll choreography.

## Scrollytelling Beat Table

| Step ID | Card heading | Card copy | data-camera | data-layer | Scrub action (0..1) |
| --- | --- | --- | --- | --- | --- |
| step-01 | Edge ingress | TLS terminates at the nearest point of presence. | cam-establish | edge-network,label-origin | 0.00 -> 1.00 |
| step-02 | Region routing | Weighted routing picks a healthy region. | cam-node | node-primary,label-node | 0.00 -> 1.00 |
| step-03 | The trunk hop | The slowest leg is the only long haul hop. | cam-trunk | edge-trunk,node-core | 0.00 -> 1.00 |
| step-04 | Customer arrival | Responses sit in the edge cache for a minute. | cam-destination | node-destination,label-arrival | 0.00 -> 1.00 |

### Camera frames

| ID | viewBox target | Purpose |
| --- | --- | --- |
| cam-establish | 0 0 1200 800 | whole network orientation |
| cam-node | 420 180 420 300 | push into the primary node |
| cam-trunk | 180 300 760 420 | follow the trunk edge |
| cam-destination | 700 260 420 320 | arrive at the destination |

### Motion budget

- Camera transitions: 900ms with --ease-out, cancel and restart from the
  current viewBox coordinates.
- Layer transitions: 240ms opacity, 320ms transform.
- Reduced motion: instant cuts, layers appear without transform.
"""

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meridian edge network - where a request stalls</title>
<style>
  :root {
    --brand-hue: 24;
    --accent-hue: 196;
    --surface-bg: oklch(0.985 0.004 var(--brand-hue));
    --surface-border: oklch(0.88 0.010 var(--brand-hue));
    --ink-primary: oklch(0.21 0.018 var(--brand-hue));
    --ink-accent: oklch(0.58 0.17 var(--accent-hue));
    --font-display: "Instrument Serif", Georgia, serif;
    --font-body: "Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif;
    --text-hero: clamp(2.75rem, 1.10rem + 7.2vw, 7.5rem);
    --text-body: clamp(1rem, 0.94rem + 0.28vw, 1.125rem);
    --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
  }

  *, *::before, *::after { box-sizing: border-box; min-width: 0; }
  html, body { overflow-x: clip; }
  body {
    margin: 0;
    background: var(--surface-bg);
    color: var(--ink-primary);
    font-family: var(--font-body);
    font-size: var(--text-body);
  }
  h1, h2 { text-wrap: balance; font-family: var(--font-display); }
  p { text-wrap: pretty; max-width: 65ch; }
  .hero { padding: 6rem 1rem; }
  .hero h1 { font-size: var(--text-hero); line-height: 1.02; margin: 0 0 1rem; }
  .story { display: grid; grid-template-columns: 4fr 8fr; gap: 2rem; }
  .steps { display: grid; gap: 18vh; padding-block: 16vh; }
  .step { opacity: 0.42; transition: opacity 200ms var(--ease-out); }
  .step.is-active { opacity: 1; }
  .stage { position: sticky; top: 0; height: 100vh; }
  .edge { fill: none; stroke: var(--ink-accent); stroke-width: 2; }
  .node { fill: var(--ink-primary); }
  .label { font-family: "JetBrains Mono", monospace; font-size: 15px; }
  .btn {
    min-height: 44px;
    min-width: 44px;
    padding: 0.9rem 1.6rem;
    border: 1px solid var(--ink-primary);
    border-radius: 999px;
    background: var(--ink-primary);
    color: var(--surface-bg);
    cursor: pointer;
  }
  .btn:hover { background: var(--ink-accent); border-color: var(--ink-accent); }
  .btn:focus-visible { outline: 2px solid var(--ink-accent); outline-offset: 2px; }
  .btn:active { transform: translateY(1px); }
  .btn[disabled] { opacity: 0.5; cursor: not-allowed; }

  @media (max-width: 900px) {
    .story { grid-template-columns: 1fr; }
    .stage { height: 62vh; }
  }

  @media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
    .step { opacity: 1; }
  }
</style>
</head>
<body>

<header class="hero">
  <h1>A request leaves the edge in 4&nbsp;ms</h1>
  <p>Every call your backend makes crosses four boundaries before it reaches a
  customer. Here is the path, and the three places it can stall.</p>
</header>

<main>
  <section class="story" aria-label="How a request travels">
    <div class="steps">
      <article class="step" id="step-01" data-step="step-01" data-camera="cam-establish" data-layer="edge-network,label-origin">
        <h2>Edge ingress</h2>
        <p>TLS terminates at the nearest point of presence and the request is
        authenticated against the signed deployment certificate.</p>
      </article>

      <article class="step" id="step-02" data-step="step-02" data-camera="cam-node" data-layer="node-primary,label-node">
        <h2>Region routing</h2>
        <p>Weighted routing picks a healthy region, and unhealthy regions drain
        within one health check interval.</p>
      </article>

      <article class="step" id="step-03" data-step="step-03" data-camera="cam-trunk" data-layer="edge-trunk,node-core">
        <h2>The trunk hop</h2>
        <p>The slowest leg is almost always the single long haul hop, so this
        is the one network path worth profiling.</p>
      </article>

      <article class="step" id="step-04" data-step="step-04" data-camera="cam-destination" data-layer="node-destination,label-arrival">
        <h2>Customer arrival</h2>
        <p>Responses sit in the edge cache for sixty seconds by default, which
        remains the cheapest latency win available to most teams.</p>
      </article>
    </div>

    <figure class="stage" id="stage">
      <svg id="map" viewBox="0 0 1200 800" role="img" aria-labelledby="map-title map-desc">
        <title id="map-title">Meridian edge network topology</title>
        <desc id="map-desc">A schematic of four points of presence, the trunk
        link between eu-west and us-east, and the customer node in ap-south.</desc>

        <rect id="cam-establish" x="0" y="0" width="1200" height="800" opacity="0" fill="none"></rect>
        <rect id="cam-node" x="420" y="180" width="420" height="300" opacity="0" fill="none"></rect>
        <rect id="cam-trunk" x="180" y="300" width="760" height="420" opacity="0" fill="none"></rect>
        <rect id="cam-destination" x="700" y="260" width="420" height="320" opacity="0" fill="none"></rect>

        <g id="edge-network" class="layer">
          <path class="edge" d="M180 520 C 380 380, 700 300, 1010 420" stroke-dasharray="6 8"></path>
        </g>
        <g id="label-origin" class="layer">
          <text class="label" x="150" y="560">eu-west / fra</text>
        </g>
        <g id="node-primary" class="layer">
          <circle class="node" cx="180" cy="520" r="12"></circle>
        </g>
        <g id="label-node" class="layer">
          <text class="label" x="470" y="360">us-east / iad</text>
        </g>
        <g id="edge-trunk" class="layer">
          <path class="edge" d="M620 400 L 760 480" stroke-width="4"></path>
        </g>
        <g id="node-core" class="layer">
          <rect class="node" x="600" y="370" width="46" height="46" rx="8"></rect>
        </g>
        <g id="node-destination" class="layer">
          <path class="node" d="M760 640 l 30 -52 30 52 z"></path>
        </g>
        <g id="label-arrival" class="layer">
          <text class="label" x="730" y="700">customer / sin</text>
        </g>
      </svg>
      <figcaption class="meter"><span id="meter-fill"></span></figcaption>
    </figure>
  </section>
</main>

<footer class="hero">
  <button class="btn" type="button">Start a 14 day trace trial</button>
</footer>

<script type="module">
  const svg = document.getElementById('map');
  const stage = document.getElementById('stage');
  const steps = Array.from(document.querySelectorAll('[data-step]'));
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const CAMERA_MS = 900;

  const cubicOut = (t) => 1 - Math.pow(1 - t, 3);
  const lerp = (a, b, t) => a + (b - a) * t;
  let frame = 0;
  let activeId = null;

  function readViewBox() {
    const [x, y, w, h] = svg.getAttribute('viewBox').split(/\\s+/).map(Number);
    return { x, y, w, h };
  }

  function applyViewBox(vb) {
    const round = (n) => Math.round(n * 100) / 100;
    svg.setAttribute('viewBox', [vb.x, vb.y, vb.w, vb.h].map(round).join(' '));
  }

  function moveCamera(targetId) {
    const target = stage.querySelector('#' + CSS.escape(targetId));
    if (!target) throw new Error('missing camera id: ' + targetId);
    if (frame) { cancelAnimationFrame(frame); frame = 0; }
    const from = readViewBox();
    const to = {
      x: Number(target.getAttribute('x')),
      y: Number(target.getAttribute('y')),
      w: Number(target.getAttribute('width')),
      h: Number(target.getAttribute('height'))
    };
    if (reducedMotion.matches) { applyViewBox(to); return; }
    const t0 = performance.now();
    const tick = (now) => {
      const t = Math.min((now - t0) / CAMERA_MS, 1);
      const e = cubicOut(t);
      applyViewBox({
        x: lerp(from.x, to.x, e),
        y: lerp(from.y, to.y, e),
        w: lerp(from.w, to.w, e),
        h: lerp(from.h, to.h, e)
      });
      frame = t < 1 ? requestAnimationFrame(tick) : 0;
    };
    frame = requestAnimationFrame(tick);
  }

  function setLayers(card) {
    const wanted = new Set((card.dataset.layer || '').split(',').map((v) => v.trim()).filter(Boolean));
    stage.querySelectorAll('.layer').forEach((node) => {
      node.style.opacity = wanted.has(node.id) ? '1' : '0';
    });
  }

  function activate(card) {
    if (activeId === card.dataset.step) return;
    activeId = card.dataset.step;
    steps.forEach((s) => s.classList.toggle('is-active', s === card));
    setLayers(card);
    moveCamera(card.dataset.camera || 'cam-establish');
  }

  const observer = new IntersectionObserver(
    (entries) => { for (const entry of entries) if (entry.isIntersecting) activate(entry.target); },
    { rootMargin: '-35% 0px -55% 0px', threshold: 0 }
  );

  steps.forEach((card) => {
    const missing = [];
    const camera = card.dataset.camera;
    if (camera && !stage.querySelector('#' + CSS.escape(camera))) missing.push(camera);
    for (const layer of (card.dataset.layer || '').split(',')) {
      const id = layer.trim();
      if (id && !stage.querySelector('#' + CSS.escape(id))) missing.push(id);
    }
    if (missing.length) throw new Error('step ' + card.dataset.step + ' references missing ids: ' + missing.join(', '));
    observer.observe(card);
  });
</script>

</body>
</html>
"""

REPORT_TEMPLATE = """# 06 Gauntlet Report

Project: the four-hop edge request story for platform engineers.
Entry under test: index.html
Command: node skills/frontend-studio-gauntlet/scripts/playwright_gauntlet.js --url ./index.html --out .studio/screenshots

## Desktop Screenshot

- Viewport: 1440x900
- File: .studio/screenshots/desktop-1440x900.png
- Page height at capture: 6420px
- First-viewport focal point: the live trace crossing the stage frame

## Mobile Screenshot

- Viewport: 390x844
- File: .studio/screenshots/mobile-390x844.png
- Reflow notes: the 4/8 story split collapses to one column, stage pins at 62vh

## Console / Page Errors

- console.error count: 0
- pageerror count: 0
- Broken images: 0 of 0
- Details: none

## Horizontal Overflow Check

| Viewport | innerWidth | scrollWidth | Pass |
| --- | --- | --- | --- |
| 1440x900 | 1440 | 1440 | yes |
| 390x844 | 390 | 390 | yes |

## Scrollytelling Step Activation

| Step | Reached active state | Active selector observed |
| --- | --- | --- |
| step-01 | yes | is-active |
| step-02 | yes | is-active |
| step-03 | yes | is-active |
| step-04 | yes | is-active |

Activation rate: 4/4

## Reference Bar Compared

- Primary Bar: The Pudding edge network scrollytelling, https://pudding.cool/
- Secondary Bar: Stripe Sessions developer hero, https://stripe.com/sessions
- Comparison performed with labels stripped: yes

| Axis | Our render | Primary Bar | Gap | Verdict |
| --- | --- | --- | --- | --- |
| A. Hero focal point | 8 | 9 | 1 | pass |
| B. Section rhythm variance | 8 | 9 | 1 | pass |
| C. Typographic tension | 7 | 9 | 2 | pass |
| D. Coco Chanel polish | 6 | 9 | 3 | fail before fix |

## Round 1 Critic Findings & Fixes Applied

Weakest axis: D

| # | Finding | Fix applied | Evidence | Rerun checks |
| --- | --- | --- | --- | --- |
| 1 | The stage card carried a redundant border and a soft shadow on top of a hairline. | Removed the decorative border and kept a single hairline on the stage frame. | index.html .stage rule, desktop screenshot before and after | pass |
| 2 | The hero meta baseline floated 6px above the h1 cap height. | Aligned the meta block baseline to the display cap height on the 7/5 grid. | index.html .hero rule | pass |

Round 2 re-capture: desktop-1440x900.png and mobile-390x844.png after fixes
Automated checks after fixes: console 0, pageerror 0, overflow pass

## Final Verdict

Verdict: WIN

The render clears the Stage 2 bar on every axis after one polish pass: the hero
focal point is unambiguous, the five sections alternate archetype and density,
the display and body faces hold a real hierarchy, and the redundant decorative
chrome flagged in Round 1 is gone.
"""


def run_gate(phase, studio_dir, target=None, cwd=None):
    """Invoke verify_gate.py as a subprocess and return the CompletedProcess."""
    command = [sys.executable, str(VERIFY_GATE), "--phase", str(phase), "--dir", str(studio_dir)]
    if target is not None:
        command += ["--target", str(target)]
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


class GateTestCase(unittest.TestCase):
    """Base fixture providing a fully valid studio directory and page."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.studio = self.root / ".studio"
        self.studio.mkdir(parents=True, exist_ok=True)

        self.write("01-BRIEF.md", BRIEF_TEMPLATE)
        self.write("02-MOODBOARD.md", MOODBOARD_TEMPLATE)
        self.write("03-TOKENS.css", TOKENS_TEMPLATE)
        self.write("04-BEAT-SHEET.md", BEAT_SHEET_TEMPLATE)
        self.write("06-GAUNTLET-REPORT.md", REPORT_TEMPLATE)
        self.write_page("index.html", PAGE_TEMPLATE)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, content):
        (self.studio / name).write_text(content, encoding="utf-8")

    def write_page(self, name, content):
        (self.root / name).write_text(content, encoding="utf-8")

    def studio_text(self, name):
        return (self.studio / name).read_text(encoding="utf-8")

    def page_text(self, name="index.html"):
        return (self.root / name).read_text(encoding="utf-8")

    def page_path(self, name="index.html"):
        return self.root / name

    # assertions ------------------------------------------------------------

    def assert_gate_passes(self, phase, target=None, message=""):
        result = run_gate(phase, self.studio, target, cwd=self.root)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"phase {phase} should pass{message}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )
        self.assertIn(
            PHASE_MESSAGES[phase],
            result.stdout,
            msg=f"phase {phase} did not print its exact PASS line{message}",
        )
        return result

    def assert_gate_fails(self, phase, target=None, contains=None, message=""):
        result = run_gate(phase, self.studio, target, cwd=self.root)
        self.assertEqual(
            result.returncode,
            1,
            msg=f"phase {phase} should fail{message}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )
        if contains:
            self.assertIn(
                contains,
                result.stdout + result.stderr,
                msg=f"phase {phase} failure should mention {contains!r}{message}",
            )
        return result


class TestRepositoryLayout(unittest.TestCase):
    """The repo itself must satisfy its own progressive disclosure contract."""

    longMessage = False

    def test_required_files_exist(self):
        required = [
            REPO_ROOT / "README.md",
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "CLAUDE.md",
            REPO_ROOT / ".gitignore",
            SYNC_SCRIPT,
            HUB_SKILL,
            VERIFY_GATE,
            SKILL_DIR / "scripts" / "playwright_gauntlet.js",
            Path(__file__).resolve(),
        ]
        required += sorted(SPOKE_DIR.glob("spoke-0*.md"))
        for path in required:
            with self.subTest(path=str(path)):
                self.assertTrue(path.is_file(), f"missing required file: {path}")

    def test_exactly_five_spokes_with_expected_names(self):
        names = sorted(p.name for p in SPOKE_DIR.glob("spoke-*.md"))
        self.assertEqual(
            names,
            [
                "spoke-01-inspiration.md",
                "spoke-02-tokens-antislop.md",
                "spoke-03-scrollytelling-layout.md",
                "spoke-04-implementation-craft.md",
                "spoke-05-gauntlet-verification.md",
            ],
        )

    def test_scripts_are_executable(self):
        self.assertTrue(os.access(VERIFY_GATE, os.X_OK), "verify_gate.py must be chmod +x")
        self.assertTrue(os.access(SYNC_SCRIPT, os.X_OK), "sync_harnesses.sh must be chmod +x")

    def test_hub_skill_stays_under_260_lines(self):
        lines = HUB_SKILL.read_text(encoding="utf-8").splitlines()
        self.assertLess(
            len(lines),
            260,
            "the hub must stay under 260 lines or it causes context rot",
        )
        self.assertGreater(len(lines), 80, "the hub must actually carry the orchestration rules")

    def test_hub_skill_has_no_em_or_en_dashes(self):
        text = HUB_SKILL.read_text(encoding="utf-8")
        for dash, name in (("\u2014", "em dash"), ("\u2013", "en dash")):
            with self.subTest(dash=name):
                self.assertNotIn(dash, text, f"SKILL.md must not contain a {name}")

    def test_hub_skill_frontmatter(self):
        text = HUB_SKILL.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"), "SKILL.md must open with YAML frontmatter")
        frontmatter = text.split("---", 2)[1]
        self.assertIn("name: frontend-studio-gauntlet", frontmatter)
        description_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
        self.assertIsNotNone(description_match, "SKILL.md frontmatter needs a description")
        description = description_match.group(1).strip()
        self.assertLess(len(description), 1024, "description must stay under 1024 characters")
        self.assertGreater(len(description), 80, "description must be specific")

    def test_hub_routes_all_six_stages_and_five_spokes(self):
        text = HUB_SKILL.read_text(encoding="utf-8")
        for stage in range(1, 7):
            with self.subTest(stage=stage):
                self.assertIn(f"Stage {stage}", text)
        for spoke in sorted(SPOKE_DIR.glob("spoke-0*.md")):
            with self.subTest(spoke=spoke.name):
                self.assertIn(spoke.name, text)
        self.assertIn(
            "GATE 6 PASSED: ALL FRONTEND STUDIO CRITERIA VERIFIED",
            text,
            "the hub must quote the exact Phase 6 completion line",
        )

    def test_no_filler_copy_or_unfinished_stubs_in_executable_sources(self):
        """The shipped scripts model full output: no filler, no open stubs.

        The validator legitimately spells the banned strings out as regex
        literals, and the markdown deliberately quotes the ban list, so this
        scans the three executable sources where filler would be a real defect.
        """
        forbidden = (
            "Lorem ipsum dolor",
            "dolor sit amet, consectetur adipiscing",
            "Lorem Inc",
            "Acme Corp",
            "Your text here",
            "TODO: implement",
            "TODO: fill",
            "FIXME: fix",
            "rest of the implementation",
            "rest of the code",
        )
        targets = [
            VERIFY_GATE,
            SYNC_SCRIPT,
            SKILL_DIR / "scripts" / "playwright_gauntlet.js",
        ]
        for path in targets:
            text = path.read_text(encoding="utf-8")
            for needle in forbidden:
                with self.subTest(path=path.name, needle=needle):
                    self.assertNotIn(
                        needle, text, f"{path} contains banned filler {needle!r}"
                    )

    def test_verify_gate_uses_standard_library_only(self):
        text = VERIFY_GATE.read_text(encoding="utf-8")
        imports = set(re.findall(r"^\s*(?:from|import)\s+([A-Za-z_][\w.]*)", text, re.MULTILINE))
        allowed = {"argparse", "pathlib", "re", "sys", "__future__"}
        self.assertTrue(
            imports <= allowed,
            f"verify_gate.py must use the standard library only, found: {sorted(imports - allowed)}",
        )


class TestHappyPath(GateTestCase):
    """A valid studio plus a valid scrollytelling page passes every gate."""

    def test_each_phase_passes_in_isolation(self):
        for phase in range(1, 5):
            with self.subTest(phase=phase):
                self.assert_gate_passes(phase)
        self.assert_gate_passes(5, self.page_path())
        self.assert_gate_passes(6, self.page_path())

    def test_phase_six_prints_the_exact_completion_line(self):
        result = self.assert_gate_passes(6, self.page_path())
        self.assertEqual(
            result.stdout.count("GATE 6 PASSED: ALL FRONTEND STUDIO CRITERIA VERIFIED"),
            1,
            "the completion line must be printed exactly once",
        )
        self.assertEqual(result.returncode, 0)

    def test_gates_are_cumulative(self):
        # Deleting a Phase 1 artifact must fail Phase 4, 5 and 6 even though
        # their own artifacts are intact.
        (self.studio / "01-BRIEF.md").unlink()
        for phase in (4, 5, 6):
            with self.subTest(phase=phase):
                result = run_gate(phase, self.studio, self.page_path(), cwd=self.root)
                self.assertEqual(result.returncode, 1)
                self.assertIn("GATE 1 FAILED", result.stdout)

    def test_phase_five_accepts_a_source_directory_target(self):
        src = self.root / "src"
        src.mkdir()
        (src / "stage.html").write_text(self.page_text(), encoding="utf-8")
        (src / "tokens.css").write_text(self.studio_text("03-TOKENS.css"), encoding="utf-8")
        self.assert_gate_passes(5, src)

    def test_phase_five_ignores_node_modules(self):
        junk = self.root / "node_modules" / "pkg"
        junk.mkdir(parents=True)
        (junk / "broken.js").write_text("TODO: not our code\n", encoding="utf-8")
        self.assert_gate_passes(5, self.root)


class TestPhaseOne(GateTestCase):
    def test_fails_when_dial_integers_are_missing(self):
        brief = self.studio_text("01-BRIEF.md")
        brief = brief.replace("- DESIGN_VARIANCE: 7", "- DESIGN_VARIANCE: TBD")
        brief = brief.replace("- MOTION_INTENSITY: 6", "- MOTION_INTENSITY: TBD")
        brief = brief.replace("- VISUAL_DENSITY: 7", "- VISUAL_DENSITY: TBD")
        self.write("01-BRIEF.md", brief)
        self.assert_gate_fails(1, contains="states no explicit integer rating")

    def test_fails_when_a_dial_is_out_of_range(self):
        brief = self.studio_text("01-BRIEF.md").replace("MOTION_INTENSITY: 6", "MOTION_INTENSITY: 42")
        self.write("01-BRIEF.md", brief)
        self.assert_gate_fails(1, contains="integers from 1 to 10")

    def test_fails_when_the_brief_is_missing(self):
        (self.studio / "01-BRIEF.md").unlink()
        self.assert_gate_fails(1, contains="required artifact missing")

    def test_fails_when_the_brief_is_too_thin(self):
        self.write("01-BRIEF.md", "# 01 Brief\n\nDESIGN_VARIANCE: 5\n")
        self.assert_gate_fails(1, contains="too thin")

    def test_fails_when_the_archetype_heading_is_missing(self):
        brief = self.studio_text("01-BRIEF.md").replace("Aesthetic Archetype", "Look and feel")
        self.write("01-BRIEF.md", brief)
        self.assert_gate_fails(1, contains="Aesthetic Archetype")

    def test_fails_on_a_placeholder_in_the_brief(self):
        brief = self.studio_text("01-BRIEF.md") + "\nTODO: confirm the audience with sales.\n"
        self.write("01-BRIEF.md", brief)
        self.assert_gate_fails(1, contains="banned placeholder or truncation stub")


class TestPhaseTwo(GateTestCase):
    def test_fails_when_reference_urls_are_missing(self):
        moodboard = self.studio_text("02-MOODBOARD.md")
        moodboard = moodboard.replace("https://pudding.cool/", "")
        moodboard = moodboard.replace("https://stripe.com/sessions", "")
        self.write("02-MOODBOARD.md", moodboard)
        self.assert_gate_fails(2, contains="no http:// or https:// reference URL")

    def test_fails_when_a_required_heading_is_missing(self):
        moodboard = self.studio_text("02-MOODBOARD.md").replace("Typography Behavior", "Type notes")
        self.write("02-MOODBOARD.md", moodboard)
        self.assert_gate_fails(2, contains="Typography Behavior")

    def test_fails_when_the_moodboard_is_too_thin(self):
        self.write("02-MOODBOARD.md", "# 02 Moodboard\n\n## Primary Bar\n\nhttps://example.com\n")
        self.assert_gate_fails(2, contains="too thin")


class TestPhaseThree(GateTestCase):
    def test_fails_on_banned_indigo_hex(self):
        tokens = self.studio_text("03-TOKENS.css").replace(
            "oklch(0.58 0.17 var(--accent-hue))", "#6366f1"
        )
        self.write("03-TOKENS.css", tokens)
        self.assert_gate_fails(3, contains="#6366f1")

    def test_fails_on_banned_purple_hex(self):
        tokens = self.studio_text("03-TOKENS.css").replace(
            "oklch(0.95 0.045 var(--accent-hue))", "#a855f7"
        )
        self.write("03-TOKENS.css", tokens)
        self.assert_gate_fails(3, contains="#a855f7")

    def test_fails_on_banned_violet_hex_in_any_case(self):
        tokens = self.studio_text("03-TOKENS.css").replace(
            "oklch(0.74 0.15 var(--accent-hue))", "#8B5CF6"
        )
        self.write("03-TOKENS.css", tokens)
        self.assert_gate_fails(3, contains="#8b5cf6")

    def test_fails_without_oklch(self):
        tokens = self.studio_text("03-TOKENS.css").replace("oklch(", "hsl(")
        self.write("03-TOKENS.css", tokens)
        self.assert_gate_fails(3, contains="oklch()")

    def test_fails_without_clamp(self):
        tokens = re.sub(
            r"^\s*--text-[a-z0-9]+: clamp\(.*$",
            "  --text-step: 1rem;",
            self.studio_text("03-TOKENS.css"),
            flags=re.MULTILINE,
        )
        self.write("03-TOKENS.css", tokens)
        self.assert_gate_fails(3, contains="clamp()")

    def test_fails_without_a_font_token(self):
        tokens = self.studio_text("03-TOKENS.css").replace("--font-", "--typeface-")
        self.write("03-TOKENS.css", tokens)
        self.assert_gate_fails(3, contains="--font-")

    def test_fails_without_hue_seeds(self):
        tokens = self.studio_text("03-TOKENS.css")
        tokens = tokens.replace("--brand-hue", "--brand").replace("--accent-hue", "--accent")
        self.write("03-TOKENS.css", tokens)
        self.assert_gate_fails(3, contains="--brand-hue")


class TestPhaseFour(GateTestCase):
    def test_fails_without_the_rhythm_heading(self):
        sheet = self.studio_text("04-BEAT-SHEET.md").replace("Page Rhythm Overview", "Layout notes")
        self.write("04-BEAT-SHEET.md", sheet)
        self.assert_gate_fails(4, contains="Page Rhythm Overview")

    def test_fails_when_the_sheet_is_too_thin(self):
        self.write("04-BEAT-SHEET.md", "# 04 Beat Sheet\n\n## Page Rhythm Overview\n\nhero\n")
        self.assert_gate_fails(4, contains="too thin")

    def test_fails_when_steps_are_declared_without_a_camera_mapping(self):
        sheet = self.studio_text("04-BEAT-SHEET.md")
        sheet = sheet.replace("data-camera", "camera target")
        self.write("04-BEAT-SHEET.md", sheet)
        self.assert_gate_fails(4, contains="beat table column mapping")


class TestPhaseFive(GateTestCase):
    def test_fails_on_todo_stub_in_source(self):
        page = self.page_text().replace(
            'type="button"', 'type="button" data-note="TODO: add the regional comparison table"'
        )
        self.write_page("index.html", page)
        self.assert_gate_fails(5, self.page_path(), contains="TODO:")

    def test_fails_on_fixme_stub_in_source(self):
        page = self.page_text() + "\n<p>FIXME: wire the retention trial form here</p>\n"
        self.write_page("index.html", page)
        self.assert_gate_fails(5, self.page_path(), contains="FIXME:")

    def test_fails_on_lorem_ipsum_in_source(self):
        page = self.page_text().replace(
            "Weighted routing picks a healthy region",
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do",
        )
        self.write_page("index.html", page)
        self.assert_gate_fails(5, self.page_path(), contains="Lorem ipsum")

    def test_fails_on_a_comment_ellipsis_stub(self):
        page = self.page_text().replace(
            "const cubicOut", "// ... rest of the easing work\n  const cubicOut"
        )
        self.write_page("index.html", page)
        self.assert_gate_fails(5, self.page_path(), contains="// ...")

    def test_fails_when_camera_id_is_orphaned(self):
        page = self.page_text().replace('data-camera="cam-trunk"', 'data-camera="cam-missing"')
        self.write_page("index.html", page)
        result = self.assert_gate_fails(5, self.page_path(), contains="orphaned scrollytelling targets")
        self.assertIn("cam-missing", result.stdout, "the failure must name the exact missing ID")

    def test_fails_when_a_layer_id_is_orphaned(self):
        page = self.page_text().replace("edge-trunk,node-core", "edge-trunk,node-ghost")
        self.write_page("index.html", page)
        result = self.assert_gate_fails(5, self.page_path(), contains="orphaned scrollytelling targets")
        self.assertIn("node-ghost", result.stdout, "the failure must name the exact missing layer ID")

    def test_reports_every_orphan_at_once(self):
        page = self.page_text()
        page = page.replace('data-camera="cam-node"', 'data-camera="cam-alpha"')
        page = page.replace("node-destination,label-arrival", "node-delta,label-epsilon")
        self.write_page("index.html", page)
        result = self.assert_gate_fails(5, self.page_path())
        for orphan in ("cam-alpha", "node-delta", "label-epsilon"):
            self.assertIn(orphan, result.stdout)

    def test_fails_without_prefers_reduced_motion(self):
        page = self.page_text()
        page = page.replace(
            "@media (prefers-reduced-motion: reduce) {", "@media (min-width: 0px) {"
        )
        page = page.replace(
            "const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');",
            "const reducedMotion = window.matchMedia('(min-width: 0px)');",
        )
        self.assertNotIn("prefers-reduced-motion", page, "fixture setup must remove every mention")
        self.write_page("index.html", page)
        self.assert_gate_fails(5, self.page_path(), contains="prefers-reduced-motion")

    def test_fails_when_target_is_missing(self):
        self.assert_gate_fails(5, contains="requires --target")

    def test_fails_when_target_has_no_sources(self):
        empty = self.root / "empty"
        empty.mkdir()
        self.assert_gate_fails(5, empty, contains="no source files found")

    def test_detects_orphans_across_multiple_files(self):
        src = self.root / "src"
        src.mkdir()
        (src / "steps.html").write_text(
            '<article data-step="step-01" data-camera="cam-missing"></article>\n',
            encoding="utf-8",
        )
        (src / "stage.js").write_text("export const noop = () => {};\n", encoding="utf-8")
        self.assert_gate_fails(5, src, contains="cam-missing")

    def test_accepts_single_quoted_attributes(self):
        page = self.page_text().replace('data-camera="cam-trunk"', "data-camera='cam-trunk'")
        self.write_page("index.html", page)
        self.assert_gate_passes(5, self.page_path())


class TestPhaseSix(GateTestCase):
    def test_fails_without_a_win_verdict(self):
        report = self.studio_text("06-GAUNTLET-REPORT.md").replace(
            "Verdict: WIN", "Verdict: BLOCKED because Chromium is unavailable"
        )
        self.write("06-GAUNTLET-REPORT.md", report)
        self.assert_gate_fails(6, self.page_path(), contains="records a BLOCKED verdict")

    def test_fails_when_a_required_heading_is_missing(self):
        report = self.studio_text("06-GAUNTLET-REPORT.md").replace(
            "Horizontal Overflow Check", "Overflow"
        )
        self.write("06-GAUNTLET-REPORT.md", report)
        self.assert_gate_fails(6, self.page_path(), contains="Horizontal Overflow Check")

    def test_fails_when_the_report_is_missing(self):
        (self.studio / "06-GAUNTLET-REPORT.md").unlink()
        self.assert_gate_fails(6, self.page_path(), contains="required artifact missing")

    def test_phase_six_reverifies_the_implementation(self):
        self.write_page("index.html", self.page_text().replace('data-camera="cam-trunk"', 'data-camera="cam-gone"'))
        result = run_gate(6, self.studio, self.page_path(), cwd=self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("GATE 5 FAILED", result.stdout)
        self.assertNotIn("GATE 6 PASSED", result.stdout)


class TestCliSurface(unittest.TestCase):
    def test_help_works(self):
        result = subprocess.run(
            [sys.executable, str(VERIFY_GATE), "--help"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--phase", result.stdout)
        self.assertIn("--target", result.stdout)

    def test_rejects_an_out_of_range_phase(self):
        result = subprocess.run(
            [sys.executable, str(VERIFY_GATE), "--phase", "9", "--dir", "."],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)

    def test_fails_when_the_studio_directory_is_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / ".studio" / "not-created"
            result = subprocess.run(
                [sys.executable, str(VERIFY_GATE), "--phase", "1", "--dir", str(missing)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("studio directory not found", result.stderr)


REACT_TSX_PAGE = '''"use client";

import { useEffect, useRef } from "react";

type Step = {
  id: string;
  heading: string;
  copy: string;
  camera: string;
  layers: string[];
};

const STEPS: Step[] = [
  {
    id: "step-01",
    heading: "Edge ingress",
    copy: "TLS terminates at the nearest point of presence.",
    camera: "cam-establish",
    layers: ["edge-network", "label-origin"],
  },
  {
    id: "step-02",
    heading: "Region routing",
    copy: "Weighted routing picks a healthy region.",
    camera: "cam-node",
    layers: ["node-primary"],
  },
];

export function NetworkStage() {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    const svg = svgRef.current;
    if (!svg) return;
  }, []);

  return (
    <section className="story" aria-label="How a request travels">
      <div className="steps">
        {STEPS.map((step) => (
          <article
            key={step.id}
            id={step.id}
            data-step={step.id}
            data-camera={step.camera}
            data-layer={step.layers.join(",")}
            className="step opacity-40"
          >
            <h2>{step.heading}</h2>
            <p>{step.copy}</p>
          </article>
        ))}
      </div>

      <figure id="stage" className="stage sticky top-0 h-screen">
        <svg ref={svgRef} viewBox="0 0 1200 800" role="img" aria-label="Edge network topology">
          <rect id="cam-establish" x="0" y="0" width="1200" height="800" opacity="0" fill="none" />
          <rect id="cam-node" x="420" y="180" width="420" height="300" opacity="0" fill="none" />
          <g id="edge-network" className="layer">
            <path d="M180 520 C 380 380, 700 300, 1010 420" className="edge" />
          </g>
          <g id="label-origin" className="layer">
            <text x="150" y="560">eu-west / fra</text>
          </g>
          <g id="node-primary" className="layer">
            <circle cx="180" cy="520" r="12" className="node" />
          </g>
        </svg>
      </figure>
    </section>
  );
}
'''


class TestAuditRegressions(GateTestCase):
    """Regression coverage for the post-audit hardening pass."""

    def test_phase_three_fails_on_banned_terracotta_hex(self):
        tokens = self.studio_text("03-TOKENS.css").replace(
            "oklch(0.58 0.17 var(--accent-hue))", "#d97757"
        )
        self.write("03-TOKENS.css", tokens)
        result = self.assert_gate_fails(3, contains="#d97757")
        self.assertIn(
            "banned AI-default hex code", result.stdout, "the failure must name the ban rule"
        )

    def test_phase_four_fails_when_motion_intensity_high_but_no_steps(self):
        # The brief keeps MOTION_INTENSITY at 6, so the beat sheet is mandatory.
        self.assertIn("MOTION_INTENSITY: 6", self.studio_text("01-BRIEF.md"))

        sheet = self.studio_text("04-BEAT-SHEET.md")
        # Strip every scrollytelling trace: step ids, data-camera column, and
        # the camera frame table, leaving a purely static rhythm sheet.
        sheet = sheet.replace("| step-0", "| beat-0")
        sheet = sheet.replace("data-camera", "target region")
        sheet = re.sub(r"^### Camera frames.*?(?=^### )", "", sheet, flags=re.S | re.M)
        self.assertNotIn("data-step", sheet)
        self.write("04-BEAT-SHEET.md", sheet)

        result = self.assert_gate_fails(4, contains="MOTION_INTENSITY")
        self.assertIn("Scrollytelling Beat Table is mandatory", result.stdout)

    def test_phase_five_catches_orphans_in_react_tsx_step_arrays(self):
        src = self.root / "src"
        src.mkdir()
        tsx = src / "NetworkStage.tsx"
        tsx.write_text(REACT_TSX_PAGE, encoding="utf-8")
        (src / "globals.css").write_text(
            "@media (prefers-reduced-motion: reduce) { "
            "* { transition-duration: 0.01ms !important; } }\n",
            encoding="utf-8",
        )
        self.assert_gate_passes(5, src, message=" for a clean React step array")

        # A camera id that exists nowhere in the SVG stage.
        broken = tsx.read_text(encoding="utf-8").replace(
            'camera: "cam-node"', 'camera: "cam-missing"'
        )
        tsx.write_text(broken, encoding="utf-8")
        result = self.assert_gate_fails(5, src, contains="cam-missing")
        self.assertIn(
            "orphaned scrollytelling targets",
            result.stdout,
            "JSX object-literal cameras must be reconciled like HTML attributes",
        )

        # A layer id that exists nowhere in the SVG stage.
        broken_layer = tsx.read_text(encoding="utf-8").replace(
            'layers: ["node-primary"]', 'layers: ["node-primary", "node-ghost"]'
        )
        tsx.write_text(broken_layer, encoding="utf-8")
        self.assert_gate_fails(5, src, contains="node-ghost")

    def test_phase_five_fails_on_acme_corp_filler(self):
        page = self.page_text().replace(
            "Start a 14 day trace trial", "Start your Acme Corp trial"
        )
        self.assertIn("Acme Corp", page, "fixture setup must inject the filler")
        self.write_page("index.html", page)
        self.assert_gate_fails(5, self.page_path(), contains="Acme-Corp")

    def test_phase_six_rejects_unedited_win_blocked_template(self):
        report = self.studio_text("06-GAUNTLET-REPORT.md").replace(
            "Verdict: WIN", "Verdict: <WIN | BLOCKED>"
        )
        self.write("06-GAUNTLET-REPORT.md", report)
        result = self.assert_gate_fails(6, self.page_path())
        self.assertIn(
            "unedited template verdict", result.stdout,
            "the literal <WIN | BLOCKED> must never satisfy the WIN check",
        )
        self.assertNotIn("GATE 6 PASSED", result.stdout)

    def test_phase_six_rejects_nonzero_console_or_page_errors(self):
        report = self.studio_text("06-GAUNTLET-REPORT.md").replace(
            "- console.error count: 0", "- console.error count: 5"
        )
        self.write("06-GAUNTLET-REPORT.md", report)
        result = self.assert_gate_fails(6, self.page_path())
        self.assertIn("console.error count: 5", result.stdout)

        report = self.studio_text("06-GAUNTLET-REPORT.md").replace(
            "- pageerror count: 0", "- pageerror count: 2"
        )
        self.write("06-GAUNTLET-REPORT.md", report)
        self.assert_gate_fails(6, self.page_path(), contains="pageerror count: 2")


class TestHarnessMirrors(unittest.TestCase):
    """The synced harness mirrors must be committed and in sync."""

    longMessage = False

    IGNORED_PATHS = (
        ".opencode/skills/frontend-studio-gauntlet/",
        ".agents/skills/frontend-studio-gauntlet/",
        ".claude/skills/frontend-studio-gauntlet/",
    )

    def test_gitignore_does_not_ignore_the_harness_mirrors(self):
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        active = [
            line.strip()
            for line in gitignore.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        for ignored in self.IGNORED_PATHS:
            with self.subTest(path=ignored):
                self.assertNotIn(ignored, active, f"{ignored} must be tracked, not ignored")

    def test_gitignore_still_ignores_generated_runtime_output(self):
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        for keep in (".studio/", "__pycache__/", "*.pyc", "node_modules/", ".DS_Store",
                     "screenshots/", ".playwright-gauntlet/", "report.json"):
            with self.subTest(path=keep):
                self.assertIn(keep, gitignore, f"{keep} must stay ignored")

    def test_mirrors_are_present_and_byte_identical_to_the_source(self):
        result = subprocess.run(
            ["bash", str(SYNC_SCRIPT), "--check"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"harness mirrors drifted\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )
        self.assertIn("All harness mirrors match", result.stdout)

    def test_plugin_marketplace_manifest_is_valid(self):
        manifest_path = REPO_ROOT / ".claude-plugin" / "marketplace.json"
        self.assertTrue(manifest_path.is_file(), "marketplace.json is missing")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "frontend-studio-gauntlet-marketplace")
        self.assertIn("owner", manifest)
        plugins = manifest["plugins"]
        self.assertEqual(len(plugins), 1)
        plugin = plugins[0]
        self.assertEqual(plugin["name"], "frontend-studio-gauntlet")
        self.assertRegex(plugin["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(plugin["source"], "./")
        self.assertIn("./skills/frontend-studio-gauntlet", plugin["skills"])
        for relative in plugin["skills"]:
            with self.subTest(skill=relative):
                self.assertTrue((REPO_ROOT / relative).is_dir(), f"{relative} does not exist")

    def test_gauntlet_script_uses_the_mime_safe_js_extension(self):
        scripts = SKILL_DIR / "scripts"
        self.assertTrue(
            (scripts / "playwright_gauntlet.js").is_file(),
            "playwright_gauntlet.js is required for zip MIME compatibility",
        )
        self.assertFalse(
            (scripts / "playwright_gauntlet.mjs").exists(),
            "the .mjs variant must be removed, it resolves to application/octet-stream",
        )
        source = (scripts / "playwright_gauntlet.js").read_text(encoding="utf-8")
        self.assertIn('require("node:fs")', source)
        self.assertIn('require("node:fs/promises")', source)
        self.assertIn('require("node:path")', source)
        self.assertIn('require("node:process")', source)
        self.assertIn('require("node:url")', source)
        self.assertIn('await import("playwright")', source)
        self.assertNotIn('from "node:fs"', source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
