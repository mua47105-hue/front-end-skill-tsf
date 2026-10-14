# Spoke 03: Principal UX & Motion Architect (Rhythm, Scrollytelling, Beat Sheet)

**Load this file only when you are running Stage 4.**

Stage 4 produces `.studio/04-BEAT-SHEET.md`. This file is the *spatial* source of
truth for the build. Stage 5 must implement it section for section, and
`verify_gate.py --phase 5` will mechanically verify that every `data-camera`
and `data-layer` ID named here exists in the shipped DOM.

## 1. Page Rhythm & Anti-Template Cadence

Most AI-built pages fail on **rhythm**, not color. They repeat one section
archetype until the page becomes a metronome. The eye learns the pattern in
three seconds and disengages.

Alternate **viewport density** across consecutive sections. Each section should
feel like a different room. The canonical five-section cadence:

| # | Section | Archetype | Density | Grid |
| --- | --- | --- | --- | --- |
| 1 | Hero | Asymmetric 7/5 split | medium | 7 cols copy, 5 cols media, offset baseline |
| 2 | Proof | Sticky scrollytelling stage | low text, high motion | 4 cols steps, 8 cols stage |
| 3 | Depth | High-density editorial split | high | 5 cols prose, 7 cols data table |
| 4 | Proof | Interactive proof canvas | medium | full-bleed, 3 zones, no cards |
| 5 | Resolution | Full-bleed CTA | very low | single optical center, no container |

The rule that matters: **no two adjacent sections may repeat a layout
archetype.** Specifically forbidden back-to-back:

- Two 3-column card rows. Ever.
- Two centered-text sections in a row.
- Two sections whose only difference is a swapped image.
- Two sections that both use a boxed container when one could be full-bleed.

Variance dials from Stage 1 push this further:

- `DESIGN_VARIANCE >= 7`: allow one deliberate asymmetry break per viewport, a
  section that is off the container grid on purpose.
- `VISUAL_DENSITY >= 7`: pack data, but alternate it against one very airy
  section so the page breathes.
- `VISUAL_DENSITY <= 3`: do not simply delete content; make each remaining
  block larger and give it more air.

## 2. The 5 Canonical Scrollytelling Mechanics

These are the patterns worth stealing. Names and framing follow the
`doodledood/claude-code-plugins` scrollytelling work plus The Pudding, NYT
Snow Fall, and Frontstory.

### 2.1 Graphic Sequence

Step-driven layer reveals. A static figure sits in a sticky stage; each scroll
step adds, hides, recolors, or annotates one layer. No camera, no zoom.

Use when the story is categorical: "three layers of the stack", "four failure
modes", "one funnel shown four times".

Contract: every step declares `data-layer` targets; the stage toggles opacity
and `transform` only.

### 2.2 Pan-and-Zoom SVG Camera Stage

The signature move, and the one this skill's gate cares about most. The SVG has
several invisible "camera frames" as `<rect id="cam-*" opacity="0" />`. As the
reader scrolls, an `IntersectionObserver` triggers each `[data-step]` card, and
a `requestAnimationFrame` loop interpolates the live `svg` `viewBox` from the
current coordinates to the target's coordinates using cubic easing.

Use when the story is geographic, architectural, or path-based.

Contract: each step declares `data-camera="cam-id"`; the target must exist as
an `id` inside the stage SVG.

### 2.3 Scroll-Scrubbed Progress

A continuous `0..1` progress value published as a CSS custom property,
`--scroll-progress`, driving a path draw, a meter fill, a counter, or a color
mix. No discrete steps at all.

```js
stage.style.setProperty('--scroll-progress', String(progress));
```

CSS consumes it with a registered property so the browser can interpolate:

```css
@property --scroll-progress {
  syntax: "<number>";
  inherits: true;
  initial-value: 0;
}
.meter-fill { transform: scaleX(var(--scroll-progress)); transform-origin: 0 50%; }
```

Use when the story is quantitative: performance over time, budget allocation,
cohort growth.

### 2.4 Moviescroller / Keyframed Canvas Sequence

A frame-by-frame sequence pinned to scroll. The pinned stage holds a canvas
(or a stack of positioned images) and the scroll position selects the frame
index. Scroll down plays forward, scroll up plays backward.

Use when the subject is inherently temporal: an animation studio reel, a
product assembly, a camera flythrough.

Contract: preload every frame before the pin engages, or the reader sees holes.
Never decode on scroll.

### 2.5 Show-and-Play Interactive Micro-Simulation

The reader pauses and plays. A control cluster (play/pause, scrub, speed)
drives the same stage, and scrolling away pauses it automatically.

Use when the subject is a physical or financial model: a drag-to-rotate
assembly, a flow of money, a sorting algorithm.

Contract: the play button is a real `<button>` with an accessible label, and
autoplay never starts without a user gesture.

### Choosing

- Categorical story, no camera: **2.1 Graphic Sequence**.
- Geographic or path story: **2.2 Pan-and-Zoom Camera Stage**.
- Quantitative trend: **2.3 Scroll-Scrubbed Progress**.
- Inherently temporal: **2.4 Moviescroller**.
- Hands-on model: **2.5 Show-and-Play**.
- Side-by-side comparison of peers: **2.6 Pinned Horizontal Corridor**.

Never combine 2.2 and 2.4 in one stage. Two competing pins means two competing
scroll consumers, and the reader fights the page.

### 2.6 Pinned Horizontal Gallery Corridor

The vertical page becomes a horizontal track. A `300vh` section is pinned while
its inner `100vh` track slides sideways, converting vertical scroll progress
`0..1` into a horizontal `translate3d`.

Contract: the outer section owns the scroll distance, the inner track is the
sticky viewport, and `--scroll-progress` from section 2.3 drives the
translation.

```html
<section class="corridor" id="regions" aria-label="Regional latency corridor">
  <div class="corridor__viewport">
    <div class="corridor__track" id="corridor-track">
      <article class="corridor__panel" data-corridor-panel>
        <h2>eu-west</h2>
        <p class="corridor__metric">p50 11 ms</p>
      </article>
      <article class="corridor__panel" data-corridor-panel>
        <h2>us-east</h2>
        <p class="corridor__metric">p50 38 ms</p>
      </article>
      <article class="corridor__panel" data-corridor-panel>
        <h2>ap-south</h2>
        <p class="corridor__metric">p50 74 ms</p>
      </article>
    </div>
  </div>
</section>
```

```css
.corridor { height: 300vh; position: relative; }
.corridor__viewport {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: clip;
  display: flex;
  align-items: center;
}
.corridor__track {
  display: flex;
  gap: var(--space-6);
  padding-inline: var(--space-9);
  will-change: transform;
  transform: translate3d(calc(var(--scroll-progress) * -66.66%), 0, 0);
}
.corridor__panel {
  flex: 0 0 auto;
  width: min(70vw, 720px);
  min-height: 44vh;
  padding: var(--space-7);
  border: 1px solid var(--surface-border);
  border-radius: var(--radius-lg);
  background: var(--surface-elevated);
}
```

```js
const corridor = document.getElementById('regions');
const track = document.getElementById('corridor-track');
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
const narrow = window.matchMedia('(max-width: 900px)');
let corridorFrame = 0;

function corridorEnabled() {
  return !reduced.matches && !narrow.matches;
}

function publishCorridor() {
  if (!corridorEnabled()) {
    track.style.transform = '';
    return;
  }
  const rect = corridor.getBoundingClientRect();
  const travel = rect.height - window.innerHeight;
  const progress = travel > 0 ? Math.min(Math.max(-rect.top / travel, 0), 1) : 0;
  track.style.setProperty('--scroll-progress', progress.toFixed(4));
}

function onCorridorScroll() {
  if (corridorFrame) return;
  corridorFrame = window.requestAnimationFrame(() => {
    publishCorridor();
    corridorFrame = 0;
  });
}

window.addEventListener('scroll', onCorridorScroll, { passive: true });
narrow.addEventListener('change', publishCorridor);
reduced.addEventListener('change', publishCorridor);
publishCorridor();
```

Invariants for 2.6:

- The `-66.66%` matches three panels at `70vw` plus gaps in a `100vw`
  viewport. Recompute it whenever the panel count or width changes.
- Collapse to a normal vertical stack below `900px` or under reduced motion.
  A horizontal corridor that traps scroll is a hard failure, not a preference.
- Clear `transform` entirely when disabled rather than setting it to `none`,
  so the track inherits no stale `will-change`.
- `overflow: clip` on the viewport, never `hidden`, or the sticky child breaks.
- One pinned section at a time: the corridor and the Stage 4 story stage cannot
  both pin.

## 3. Engineering Invariants for Scrollytelling

## 3. Engineering Invariants for Scrollytelling

These three invariants are what separate a working scrollytelling page from a
janky one. Stage 5 implements them; Stage 6 verifies them.

### 3.1 Any card height works

Do not hardcode step heights to match the figure. Trigger on a **viewport band**
so cards of wildly different copy lengths all fire correctly:

```js
const stepObserver = new IntersectionObserver(
  (entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) activate(entry.target);
    }
  },
  { rootMargin: '-35% 0px -55% 0px', threshold: 0 }
);
```

The band means "activate when the card's top edge crosses the line 35 percent
down the viewport, and release it once it passes 55 percent down". A short card
and a tall card both land inside that window at the right scroll position.

### 3.2 One camera move at a time

A new step **cancels** the running `requestAnimationFrame` interpolation and
starts a fresh one **from the current coordinates**, not from the original.
Restarting from the origin is what produces the nauseating double-move.

```js
let cameraFrame = 0;

function moveCamera(target) {
  if (cameraFrame) cancelAnimationFrame(cameraFrame);
  const from = readViewBox();
  const t0 = performance.now();
  const step = (now) => {
    const t = Math.min((now - t0) / CAMERA_MS, 1);
    const e = cubicOut(t);
    svg.setAttribute('viewBox', lerpViewBox(from, target, e));
    if (t < 1) cameraFrame = requestAnimationFrame(step);
    else cameraFrame = 0;
  };
  cameraFrame = requestAnimationFrame(step);
}
```

### 3.3 Loud failure on typos

Every `data-camera` value and every comma-separated `data-layer` value on a
`[data-step]` card **must** exist as an `id` in the stage. A typo is a silent
no-op at runtime, which is worse than a crash because it ships broken.

```js
function assertTargetsExist(card, stage) {
  const missing = [];
  const camera = card.dataset.camera;
  if (camera && !stage.querySelector('#' + CSS.escape(camera))) missing.push(camera);
  for (const layer of (card.dataset.layer || '').split(',')) {
    const id = layer.trim();
    if (id && !stage.querySelector('#' + CSS.escape(id))) missing.push(id);
  }
  if (missing.length) {
    throw new Error('[scrolly] step "' + card.dataset.step + '" references missing ids: ' + missing.join(', '));
  }
}
```

Call it on every step at attach time. `verify_gate.py --phase 5` performs the
same check statically and fails with the exact orphaned IDs.

### 3.4 Supporting invariants

- Register `--scroll-progress` with `@property` so it can animate and compose.
- Pin with `position: sticky` (or ScrollTrigger `pin: true`), never with a
  scroll listener that writes `top` on every frame.
- Animate only `transform`, `opacity`, and `viewBox`. Never `width`, `height`,
  `top`, or `left`.
- `scroll-behavior: smooth` on anchors, and never on the scrollytelling stage.
- Every `data-step` card needs an `id` and a heading so it is reachable by
  keyboard and by screen reader.

## 4. Template: `.studio/04-BEAT-SHEET.md`

The gate requires `Page Rhythm Overview` as a heading and 250 characters
minimum. Include the Scrollytelling Beat Table whenever `MOTION_INTENSITY >= 5`
or the page uses scrollytelling at all.

```markdown
# 04 Beat Sheet - Wireframe & Scroll Choreography

Project: <one line>
DESIGN_VARIANCE: <n>   MOTION_INTENSITY: <n>   VISUAL_DENSITY: <n>
Mechanic chosen: <Graphic Sequence | Pan-and-Zoom Camera Stage | Scroll-Scrubbed Progress | Moviescroller | Show-and-Play>

## Page Rhythm Overview

| # | Section | Archetype | Density | Grid | Focal point | Scroll intent |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Hero | Asymmetric 7/5 split | medium | 12-col, copy 7 / media 5 | <the one thing the eye hits> | introduce the promise |
| 2 | How it works | Sticky stage | low text | 12-col, steps 4 / stage 8 | pinned SVG | pin and scrub |
| 3 | Detail | Editorial split 5/7 | high | 12-col, prose 5 / table 7 | the metric row | slow read |
| 4 | Proof | Interactive canvas | medium | full-bleed | the live control | hands on |
| 5 | Resolution | Full-bleed CTA | very low | single center | the one button | convert |

Repetition ban: no two adjacent sections share a layout archetype. No two
adjacent sections may both be 3-column card rows. Section 2 is the only pinned
section.

## Hero Interactive Instrument

The first viewport is a playable centerpiece marked `data-interactive-hero`,
never a static headline plus a screenshot. State the mechanics and the bindings.

| Property | Value |
| --- | --- |
| Element | <canvas / SVG / DOM, with the `data-interactive-hero` attribute> |
| Mechanic | <shader field, spring rig, scrubbed instrument, live counter> |
| Input bindings | <pointermove, pointerdown, drag, wheel, hotkey, state toggle> |
| Uniforms or state | <what the pointer and scroll feed into> |
| Response budget | <the ms from input to visible change> |
| Reduced motion | <the still frame that replaces the loop> |
| Idle cost | <what it does when offscreen or at rest> |

## Design Spells

At least 2 signature tactile micro-interactions, each marked
`data-spell="<name>"`, chosen from spoke 6.

| Spell | Element | Trigger | Tactile result | Reduced motion |
| --- | --- | --- | --- | --- |
| <magnetic-spring> | <the button or card> | <pointer proximity> | <pulls toward cursor, overshoots back> | <no transform> |
| <hotkey-hud> | <the keycap row> | <press 1-5> | <smooth jump, keycap flash> | <instant jump> |
| <sound-toggle> | <the mute control> | <click> | <12 ms synthesized click> | <silent> |
| <analog-grain> | <the surface> | <always on> | <film grain texture> | <filter removed> |
| <liquid-refraction> | <the image> | <hover or scroll> | <turbulence displacement> | <filter removed> |
| <view-transition> | <the morph target> | <state toggle> | <morphing transition> | <direct update> |

## Scrollytelling Beat Table

Card copy is 40 words maximum. Every camera and layer ID below must exist as an
`id` in the stage markup, or Gate 5 fails.

| Step ID | Card heading | Card copy (<= 40 words) | data-camera | data-layer | Scrub action (0..1) |
| --- | --- | --- | --- | --- | --- |
| step-01 | <heading> | <copy> | cam-establish | edge-network,label-origin | 0.00 -> 1.00 |
| step-02 | <heading> | <copy> | cam-node | node-primary,label-node | 0.00 -> 1.00 |
| step-03 | <heading> | <copy> | cam-trunk | edge-trunk,node-core | 0.00 -> 1.00 |
| step-04 | <heading> | <copy> | cam-destination | node-destination,label-arrival | 0.00 -> 1.00 |

### Camera frames (invisible rects inside the stage SVG)

| ID | viewBox target | Purpose |
| --- | --- | --- |
| cam-establish | 0 0 1200 800 | whole network, reader orientation |
| cam-node | 420 180 420 300 | push into the primary node |
| cam-trunk | 180 300 760 420 | follow the trunk edge |
| cam-destination | 700 260 420 320 | arrive at the destination |

### Layer choreography

| Layer ID | Type | Enter | Exit |
| --- | --- | --- | --- |
| edge-network | path | opacity 0->1 at step 1 | holds |
| label-origin | text | fades at step 1 | fades out step 2 |
| node-primary | group | scales 0.9->1 at step 2 | holds |
| node-core | group | pops at step 3 | holds |
| node-destination | group | pops at step 4 | holds |

### Motion budget

- Transition between cameras: 900ms with `--ease-out`, cancel-and-restart from
  current coordinates.
- Layer transitions: 240ms opacity, 320ms transform.
- Reduced motion: all camera moves become instant cuts, layers appear with no
  transform, the stage still tracks scroll steps.
```

## 5. Pre-Flight Self Audit

- Every section has a distinct archetype and an explicit focal point.
- No two adjacent sections are 3-column card rows.
- Exactly one pinned section, and its mechanic is named.
- Every `data-step` has a heading, an ID, and copy under 40 words.
- Every `data-camera` and `data-layer` value listed here is an ID you will
  actually create in Stage 5.
- The scrub range on every step is documented as a `0..1` action.
- Reduced-motion behavior is specified, not assumed.

Then run:

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase 4 --dir .studio
```

Quote the printed gate line verbatim.
