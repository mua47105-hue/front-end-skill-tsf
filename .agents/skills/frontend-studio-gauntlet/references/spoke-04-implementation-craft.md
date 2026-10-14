# Spoke 04: Senior Frontend Engineer (Full-Output Production Build)

**Load this file only when you are running Stage 5.**

Stage 5 is where the page actually gets built. The bar: a complete, production
shaped, accessible, motion-aware interface that matches `.studio/04-BEAT-SHEET.md`
and consumes the tokens in `.studio/03-TOKENS.css`.

## 1. Full-Output Enforcement Protocol

### 1.1 Banned truncation

These strings fail `verify_gate.py --phase 5` in any `.html`, `.htm`, `.css`,
`.js`, `.ts`, `.jsx`, `.tsx`, `.vue`, or `.svelte` file under your target:

```text
TODO:
FIXME:
Lorem ipsum
... rest of
// ...
<!-- ... -->
```

Also banned by policy even though the gate cannot see them:

- `Acme Corp`, `Lorem Inc`, `John Doe`, `your-site-here`, `example.com`.
- `"Your text here"`, `["data"]`, `[]`, `{}` standing in for real content.
- Placeholder `#` links, `href="#"`, and buttons with no handler.
- Any section that is visually present but semantically empty.

Ship real copy at real length. If a section is long, write it long.

### 1.2 Required interactive states

Everything clickable, focusable, or draggable needs all of:

| State | Requirement |
| --- | --- |
| default | the resting visual, defined in tokens |
| `:hover` | visible change, 120 to 200ms, never a layout shift |
| `:focus-visible` | 2px ring, 2px offset, `--ink-accent`, never removed |
| `:active` | pressed offset or scale, 80 to 120ms |
| `:disabled` | 50 percent opacity, `cursor: not-allowed`, `aria-disabled` |
| empty | a designed empty state, not a blank div |
| loading | skeleton or spinner with `aria-busy="true"` |
| error | a real error message with a recovery action |

Data-driven lists must render **all three** of empty, loading, and error from
the same component, toggled by a small state variable.

### 1.3 Accessibility floor

- Semantic elements first: `header`, `nav`, `main`, `section`, `footer`,
  `figure`, `table`. `div soup` fails review.
- One `h1`. No skipped heading levels. Every `section` has an accessible name.
- Alt text describes the information, not the file name.
- Every icon-only control has `aria-label`. Decorative icons get
  `aria-hidden="true"`.
- Canvas and SVG content that carries meaning gets a `<title>` and a
  `role="img"` plus `aria-label`, or a visually hidden text alternative.
- Keyboard: the scrollytelling step list is reachable, focus order matches
  visual order, and nothing traps focus.

## 2. Skeleton 1: Zero-Dependency Vanilla JS + SVG Camera Controller

Complete, runnable, no libraries. Save as `index.html` (or split into
`index.html`, `styles.css`, `stage.js`). This is the reference implementation
of the three Stage 4 invariants.

```html
<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Meridian Edge Network - how a request reaches its destination</title>
<style>
  :root {
    color-scheme: light dark;
    --brand-hue: 24;
    --accent-hue: 196;

    --surface-bg: oklch(0.985 0.004 var(--brand-hue));
    --surface-elevated: oklch(1 0 0);
    --surface-border: oklch(0.88 0.010 var(--brand-hue));
    --ink-primary: oklch(0.21 0.018 var(--brand-hue));
    --ink-secondary: oklch(0.44 0.016 var(--brand-hue));
    --ink-accent: oklch(0.58 0.17 var(--accent-hue));
    --accent-wash: oklch(0.95 0.045 var(--accent-hue));

    --font-display: "Instrument Serif", Georgia, serif;
    --font-body: "Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif;
    --font-mono: "JetBrains Mono", ui-monospace, monospace;

    --text-hero: clamp(2.75rem, 1.10rem + 7.2vw, 7.5rem);
    --text-h1: clamp(2.25rem, 1.35rem + 3.9vw, 4.25rem);
    --text-body: clamp(1rem, 0.94rem + 0.28vw, 1.125rem);

    --space-4: 1rem;
    --space-6: 2rem;
    --space-9: 6rem;
    --radius-md: 10px;
    --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
    --dur-control: 200ms;
    --dur-camera: 900ms;
  }

  @property --scroll-progress {
    syntax: "<number>";
    inherits: true;
    initial-value: 0;
  }

  *, *::before, *::after { box-sizing: border-box; }

  html { overflow-x: clip; scroll-behavior: smooth; }
  body {
    margin: 0;
    background: var(--surface-bg);
    color: var(--ink-primary);
    font-family: var(--font-body);
    font-size: var(--text-body);
    line-height: 1.62;
    overflow-x: clip;
  }

  h1, h2 { text-wrap: balance; }
  p { text-wrap: pretty; max-width: 65ch; }

  .wrap {
    width: min(100% - 2 * var(--space-4), 1200px);
    margin-inline: auto;
  }

  .hero {
    display: grid;
    grid-template-columns: 7fr 5fr;
    gap: var(--space-6);
    align-items: end;
    padding-block: var(--space-9);
  }
  .hero h1 {
    font-family: var(--font-display);
    font-size: var(--text-hero);
    line-height: 1.02;
    letter-spacing: -0.02em;
    margin: 0 0 var(--space-4);
  }
  .hero__lede { color: var(--ink-secondary); margin: 0; }
  .hero__meta {
    font-family: var(--font-mono);
    font-size: 0.8125rem;
    color: var(--ink-secondary);
    border-left: 1px solid var(--surface-border);
    padding-left: var(--space-4);
  }

  .story { position: relative; display: grid; grid-template-columns: 4fr 8fr; gap: var(--space-6); }
  .steps { display: grid; gap: 22vh; padding-block: 18vh; }
  .step {
    border-top: 1px solid var(--surface-border);
    padding-top: var(--space-4);
    opacity: 0.42;
    transition: opacity var(--dur-control) var(--ease-out);
  }
  .step.is-active { opacity: 1; }
  .step h2 { font-size: var(--text-h1); line-height: 1.12; margin: 0 0 var(--space-4); }
  .step p { margin: 0; color: var(--ink-secondary); }

  .stage {
    position: sticky;
    top: 0;
    height: 100vh;
    display: grid;
    place-items: center;
    background: var(--surface-elevated);
    border: 1px solid var(--surface-border);
    border-radius: var(--radius-md);
    overflow: hidden;
  }
  .stage svg { width: 100%; height: 100%; }
  .stage__readout {
    font-family: var(--font-mono);
    font-size: 0.8125rem;
    color: var(--ink-secondary);
    padding: var(--space-4);
    border-top: 1px solid var(--surface-border);
  }

  .edge { fill: none; stroke: var(--ink-accent); stroke-width: 2; }
  .node { fill: var(--ink-primary); }
  .label {
    font-family: var(--font-mono);
    font-size: 15px;
    fill: var(--ink-secondary);
  }
  .layer { transition: opacity 240ms var(--ease-out), transform 320ms var(--ease-out); transform-origin: center; }
  .layer[data-off="true"] { opacity: 0; transform: scale(0.9); }

  .meter { height: 3px; background: var(--surface-border); border-radius: 999px; overflow: hidden; }
  .meter span {
    display: block; height: 100%;
    background: var(--ink-accent);
    transform: scaleX(var(--scroll-progress));
    transform-origin: 0 50%;
  }

  .cta { padding-block: var(--space-9); text-align: center; }
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.9rem 1.6rem;
    min-height: 44px;
    border-radius: 999px;
    border: 1px solid var(--ink-primary);
    background: var(--ink-primary);
    color: var(--surface-bg);
    font: inherit;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    transition: background var(--dur-control) var(--ease-out), transform var(--dur-control) var(--ease-out);
  }
  .btn:hover { background: var(--ink-accent); border-color: var(--ink-accent); }
  .btn:focus-visible { outline: 2px solid var(--ink-accent); outline-offset: 2px; }
  .btn:active { transform: translateY(1px); }

  @media (max-width: 900px) {
    .hero { grid-template-columns: 1fr; }
    .story { grid-template-columns: 1fr; }
    .stage { position: sticky; top: 0; height: 62vh; z-index: 1; }
    .steps { gap: 16vh; padding-block: 8vh; z-index: 2; }
  }

  @media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
    }
    .step { opacity: 1; }
    .layer { transition: none; }
  }
</style>
</head>
<body>

<header class="wrap hero">
  <div>
    <h1>A request leaves the edge in 4&nbsp;ms</h1>
    <p class="hero__lede">
      Every call your backend makes crosses four boundaries before it reaches a
      customer. Here is the path, and the three places it can stall.
    </p>
  </div>
  <p class="hero__meta">
    Meridian edge network<br>
    eu-west / us-east / ap-south<br>
    measured p50, 30 day window
  </p>
</header>

<main>
  <section class="story wrap" aria-label="How a request travels">
    <div class="steps">
      <article class="step" id="step-01" data-step="step-01" data-camera="cam-establish" data-layer="edge-network,label-origin">
        <h2>Edge ingress</h2>
        <p>
          TLS terminates at the nearest point of presence. The request is
          authenticated against the signed deployment certificate before a
          single byte reaches your origin.
        </p>
      </article>

      <article class="step" id="step-02" data-step="step-02" data-camera="cam-node" data-layer="node-primary,label-node">
        <h2>Region routing</h2>
        <p>
          Weighted routing picks a healthy region. Unhealthy regions drain
          within one health-check interval, so a failed zone never accumulates
          a queue in front of a healthy one.
        </p>
      </article>

      <article class="step" id="step-03" data-step="step-03" data-camera="cam-trunk" data-layer="edge-trunk,node-core">
        <h2>The trunk hop</h2>
        <p>
          The slowest leg is usually the only long-haul hop. Everything else is
          metro. If you profile one network path, profile this one.
        </p>
      </article>

      <article class="step" id="step-04" data-step="step-04" data-camera="cam-destination" data-layer="node-destination,label-arrival">
        <h2>Customer arrival</h2>
        <p>
          Responses are cached at the edge for 60 seconds by default. Raising
          that number is the cheapest latency win available to most teams.
        </p>
      </article>
    </div>

    <figure class="stage" id="stage" style="margin:0">
      <svg id="map" viewBox="0 0 1200 800" role="img" aria-labelledby="map-title map-desc" preserveAspectRatio="xMidYMid meet">
        <title id="map-title">Meridian edge network topology</title>
        <desc id="map-desc">A schematic map showing four points of presence, the trunk link between eu-west and us-east, and the destination customer node in ap-south.</desc>

        <!-- camera frames: invisible, referenced by data-camera -->
        <rect id="cam-establish" x="0" y="0" width="1200" height="800" opacity="0" fill="none"></rect>
        <rect id="cam-node" x="420" y="180" width="420" height="300" opacity="0" fill="none"></rect>
        <rect id="cam-trunk" x="180" y="300" width="760" height="420" opacity="0" fill="none"></rect>
        <rect id="cam-destination" x="700" y="260" width="420" height="320" opacity="0" fill="none"></rect>

        <g id="edge-network" class="layer" data-off="true">
          <path class="edge" d="M180 520 C 380 380, 700 300, 1010 420" stroke-dasharray="6 8"></path>
          <path class="edge" d="M1010 420 C 900 520, 820 560, 760 620" stroke-dasharray="6 8"></path>
        </g>

        <g id="label-origin" class="layer" data-off="true">
          <text class="label" x="150" y="560">eu-west / fra</text>
        </g>

        <g id="node-primary" class="layer" data-off="true">
          <circle class="node" cx="180" cy="520" r="12"></circle>
          <circle cx="180" cy="520" r="22" fill="none" stroke="var(--ink-accent)" stroke-width="2"></circle>
        </g>

        <g id="label-node" class="layer" data-off="true">
          <text class="label" x="470" y="360">us-east / iad</text>
        </g>

        <g id="edge-trunk" class="layer" data-off="true">
          <path class="edge" d="M620 400 L 760 480" stroke-width="4"></path>
        </g>

        <g id="node-core" class="layer" data-off="true">
          <rect class="node" x="600" y="370" width="46" height="46" rx="8"></rect>
        </g>

        <g id="node-destination" class="layer" data-off="true">
          <path class="node" d="M760 640 l 30 -52 30 52 z"></path>
        </g>

        <g id="label-arrival" class="layer" data-off="true">
          <text class="label" x="730" y="700">customer / sin</text>
        </g>
      </svg>
      <figcaption class="stage__readout">
        <div class="meter"><span id="meter-fill"></span></div>
        <p id="readout" style="margin:0.75rem 0 0">viewBox 0 0 1200 800</p>
      </figcaption>
    </figure>
  </section>
</main>

<footer class="wrap cta">
  <a class="btn" href="#stage">Read the latency budget</a>
</footer>

<script type="module">
  const svg = document.getElementById('map');
  const stage = document.getElementById('stage');
  const readout = document.getElementById('readout');
  const meterFill = document.getElementById('meter-fill');
  const steps = Array.from(document.querySelectorAll('[data-step]'));

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const CAMERA_MS = 900;

  const cubicOut = (t) => 1 - Math.pow(1 - t, 3);
  const lerp = (a, b, t) => a + (b - a) * t;

  let frame = 0;
  let activeId = null;

  function readViewBox() {
    const [x, y, w, h] = svg.getAttribute('viewBox').split(/\s+/).map(Number);
    return { x, y, w, h };
  }

  function applyViewBox(vb) {
    const value = `${round(vb.x)} ${round(vb.y)} ${round(vb.w)} ${round(vb.h)}`;
    svg.setAttribute('viewBox', value);
    readout.textContent = 'viewBox ' + value;
  }

  function round(n) { return Math.round(n * 100) / 100; }

  function moveCamera(targetId) {
    const target = stage.querySelector('#' + CSS.escape(targetId));
    if (!target) throw new Error('[scrolly] missing camera id: ' + targetId);

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
    const wanted = new Set(
      (card.dataset.layer || '').split(',').map((v) => v.trim()).filter(Boolean)
    );
    stage.querySelectorAll('.layer').forEach((node) => {
      node.setAttribute('data-off', String(!wanted.has(node.id)));
    });
  }

  function assertTargetsExist(card) {
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

  function activate(card) {
    if (activeId === card.dataset.step) return;
    activeId = card.dataset.step;
    steps.forEach((s) => s.classList.toggle('is-active', s === card));
    setLayers(card);
    moveCamera(card.dataset.camera || 'cam-establish');
  }

  steps.forEach((card) => {
    assertTargetsExist(card);
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) if (entry.isIntersecting) activate(entry.target);
      },
      { rootMargin: '-35% 0px -55% 0px', threshold: 0 }
    );
    observer.observe(card);
  });

  // Continuous scrub progress published as a 0..1 CSS custom property.
  const story = document.querySelector('.story');
  let ticking = false;
  const publishProgress = () => {
    const rect = story.getBoundingClientRect();
    const total = rect.height - window.innerHeight;
    const raw = total > 0 ? (-rect.top / total) : 0;
    const progress = Math.min(Math.max(raw, 0), 1);
    stage.style.setProperty('--scroll-progress', progress.toFixed(4));
    meterFill.style.setProperty('--scroll-progress', progress.toFixed(4));
    ticking = false;
  };
  window.addEventListener('scroll', () => {
    if (!ticking) { ticking = true; requestAnimationFrame(publishProgress); }
  }, { passive: true });
  window.addEventListener('resize', publishProgress);
  publishProgress();

  reducedMotion.addEventListener('change', () => {
    if (activeId) {
      const card = steps.find((s) => s.dataset.step === activeId);
      if (card) moveCamera(card.dataset.camera || 'cam-establish');
    }
  });
</script>

</body>
</html>
```

Notes on that skeleton:

- `applyViewBox` writes a single attribute per frame. No layout thrash.
- `moveCamera` cancels the previous frame **and** reads the live `viewBox` as
  the new origin, satisfying invariant 3.2.
- `assertTargetsExist` throws on a typo, satisfying invariant 3.3.
- The `IntersectionObserver` band is `-35% 0px -55% 0px`, satisfying 3.1.
- `@property --scroll-progress` plus a registered custom property lets the
  meter interpolate without JS writes per frame.

## 3. Skeleton 2: React / Next.js + Tailwind v4 + GSAP ScrollTrigger

For app-router projects. Animate only `transform` and `opacity` for 60fps.

```tsx
"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

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
    copy: "TLS terminates at the nearest point of presence and the request is authenticated against the signed deployment certificate before a byte reaches the origin.",
    camera: "cam-establish",
    layers: ["edge-network", "label-origin"],
  },
  {
    id: "step-02",
    heading: "Region routing",
    copy: "Weighted routing picks a healthy region. Unhealthy regions drain within one health-check interval, so a failed zone never queues behind a healthy one.",
    camera: "cam-node",
    layers: ["node-primary", "label-node"],
  },
  {
    id: "step-03",
    heading: "The trunk hop",
    copy: "The slowest leg is almost always the single long-haul hop. Everything else is metro, so this is the one network path worth profiling.",
    camera: "cam-trunk",
    layers: ["edge-trunk", "node-core"],
  },
  {
    id: "step-04",
    heading: "Customer arrival",
    copy: "Responses sit in the edge cache for sixty seconds by default. Raising that number remains the cheapest latency win available to most teams.",
    camera: "cam-destination",
    layers: ["node-destination", "label-arrival"],
  },
];

function readViewBox(svg: SVGSVGElement) {
  const [x, y, w, h] = svg.getAttribute("viewBox")!.split(/\s+/).map(Number);
  return { x, y, w, h };
}

export function NetworkStage() {
  const sectionRef = useRef<HTMLElement | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);
  const activeRef = useRef<string | null>(null);
  const tweenRef = useRef<gsap.core.Tween | null>(null);

  useEffect(() => {
    const section = sectionRef.current;
    const svg = svgRef.current;
    if (!section || !svg) return;

    const stage = section.querySelector("#stage")!;
    const cards = Array.from(section.querySelectorAll<HTMLElement>("[data-step]"));

    // Loud failure on typos, mirroring the vanilla invariant.
    cards.forEach((card) => {
      const camera = card.dataset.camera;
      const missing: string[] = [];
      if (camera && !stage.querySelector(`#${CSS.escape(camera)}`)) missing.push(camera);
      (card.dataset.layer ?? "").split(",").forEach((raw) => {
        const id = raw.trim();
        if (id && !stage.querySelector(`#${CSS.escape(id)}`)) missing.push(id);
      });
      if (missing.length) {
        throw new Error(`[scrolly] step "${card.dataset.step}" references missing ids: ${missing.join(", ")}`);
      }
    });

    const ctx = gsap.context(() => {
      const moveCamera = (id: string) => {
        const target = stage.querySelector(`#${CSS.escape(id)}`);
        if (!target) throw new Error(`[scrolly] missing camera id: ${id}`);

        tweenRef.current?.kill();
        const from = readViewBox(svg);
        const proxy = {
          x: from.x,
          y: from.y,
          w: from.w,
          h: from.h,
        };

        tweenRef.current = gsap.to(proxy, {
          x: Number(target.getAttribute("x")),
          y: Number(target.getAttribute("y")),
          w: Number(target.getAttribute("width")),
          h: Number(target.getAttribute("height")),
          duration: 0.9,
          ease: "power3.out",
          overwrite: true,
          onUpdate() {
            svg.setAttribute(
              "viewBox",
              `${proxy.x} ${proxy.y} ${proxy.w} ${proxy.h}`
            );
          },
        });
      };

      const setLayers = (card: HTMLElement) => {
        const wanted = new Set(
          (card.dataset.layer ?? "")
            .split(",")
            .map((v) => v.trim())
            .filter(Boolean)
        );
        stage.querySelectorAll<SVGGElement>(".layer").forEach((node) => {
          gsap.to(node, {
            opacity: wanted.has(node.id) ? 1 : 0,
            scale: wanted.has(node.id) ? 1 : 0.9,
            transformOrigin: "center",
            duration: 0.32,
            ease: "power2.out",
            overwrite: true,
          });
        });
      };

      const activate = (card: HTMLElement) => {
        const stepId = card.dataset.step!;
        if (activeRef.current === stepId) return;
        activeRef.current = stepId;

        cards.forEach((c) => c.classList.toggle("is-active", c === card));
        setLayers(card);
        moveCamera(card.dataset.camera || "cam-establish");
      };

      cards.forEach((card) => {
        ScrollTrigger.create({
          trigger: card,
          start: "top 35%",
          end: "bottom 55%",
          onEnter: () => activate(card),
          onEnterBack: () => activate(card),
        });
      });

      // Continuous scrub progress as a 0..1 value.
      const meter = section.querySelector<HTMLElement>("[data-meter]");
      if (meter) {
        ScrollTrigger.create({
          trigger: section,
          start: "top top",
          end: "bottom bottom",
          scrub: 0.3,
          onUpdate: (self) => {
            meter.style.setProperty("--scroll-progress", self.progress.toFixed(4));
          },
        });
      }

      // One pinned section for the whole story.
      ScrollTrigger.create({
        trigger: section,
        start: "top top",
        end: "+=120%",
        pin: "#stage",
        pinSpacing: true,
        anticipatePin: 1,
      });
    }, section);

    ScrollTrigger.refresh();
    return () => {
      tweenRef.current?.kill();
      ctx.revert();
    };
  }, []);

  return (
    <section ref={sectionRef} aria-label="How a request travels" className="story">
      <div className="steps">
        {STEPS.map((step) => (
          <article
            key={step.id}
            id={step.id}
            data-step={step.id}
            data-camera={step.camera}
            data-layer={step.layers.join(",")}
            className="step opacity-40 transition-opacity duration-200"
          >
            <h2 className="text-3xl font-display tracking-tight text-balance">{step.heading}</h2>
            <p className="text-pretty text-ink-secondary">{step.copy}</p>
          </article>
        ))}
      </div>

      <figure id="stage" className="stage sticky top-0 h-screen">
        <svg
          ref={svgRef}
          viewBox="0 0 1200 800"
          role="img"
          aria-labelledby="map-title map-desc"
          className="h-full w-full"
        >
          <title id="map-title">Meridian edge network topology</title>
          <desc id="map-desc">
            A schematic of four points of presence, the trunk link between
            eu-west and us-east, and the destination customer node in ap-south.
          </desc>

          <rect id="cam-establish" x="0" y="0" width="1200" height="800" opacity="0" fill="none" />
          <rect id="cam-node" x="420" y="180" width="420" height="300" opacity="0" fill="none" />
          <rect id="cam-trunk" x="180" y="300" width="760" height="420" opacity="0" fill="none" />
          <rect id="cam-destination" x="700" y="260" width="420" height="320" opacity="0" fill="none" />

          <g id="edge-network" className="layer">
            <path d="M180 520 C 380 380, 700 300, 1010 420" className="edge" strokeDasharray="6 8" />
            <path d="M1010 420 C 900 520, 820 560, 760 620" className="edge" strokeDasharray="6 8" />
          </g>
          <g id="label-origin" className="layer">
            <text x="150" y="560" className="label">eu-west / fra</text>
          </g>
          <g id="node-primary" className="layer">
            <circle cx="180" cy="520" r="12" className="node" />
          </g>
          <g id="label-node" className="layer">
            <text x="470" y="360" className="label">us-east / iad</text>
          </g>
          <g id="edge-trunk" className="layer">
            <path d="M620 400 L 760 480" className="edge" strokeWidth="4" />
          </g>
          <g id="node-core" className="layer">
            <rect x="600" y="370" width="46" height="46" rx="8" className="node" />
          </g>
          <g id="node-destination" className="layer">
            <path d="M760 640 l 30 -52 30 52 z" className="node" />
          </g>
          <g id="label-arrival" className="layer">
            <text x="730" y="700" className="label">customer / sin</text>
          </g>
        </svg>

        <figcaption data-meter className="stage-readout">
          <div className="meter">
            <span />
          </div>
        </figcaption>
      </figure>
    </section>
  );
}

export default function Page() {
  return (
    <main>
      <NetworkStage />
    </main>
  );
}
```

Tailwind v4 theme block for this component (in `app/globals.css`):

```css
@import "tailwindcss";

@theme {
  --color-surface: oklch(0.985 0.004 24);
  --color-surface-elevated: oklch(1 0 0);
  --color-ink: oklch(0.21 0.018 24);
  --color-ink-secondary: oklch(0.44 0.016 24);
  --color-accent: oklch(0.58 0.17 196);
  --font-display: "Instrument Serif", Georgia, serif;
  --font-body: "Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif;
  --text-hero: clamp(2.75rem, 1.10rem + 7.2vw, 7.5rem);
  --text-h1: clamp(2.25rem, 1.35rem + 3.9vw, 4.25rem);
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

GSAP performance rules, non-negotiable:

- Animate `transform` (x, y, scale, rotation) and `opacity` only.
- Never animate `width`, `height`, `top`, `left`, `margin`, or `filter` in a
  scroll timeline.
- Use `gsap.quickTo` or a tween proxy for the `viewBox` interpolation instead
  of writing the attribute from a raw scroll handler.
- One `pin` per scroll story. A second pin means two consumers fighting.
- Set `ScrollTrigger.config({ ignoreMobileResize: true })` when the page has a
  bottom sheet or a dynamic toolbar.

## 4. CSS Specificity & Resilient Layout Rules

### 4.1 Horizontal overflow is a hard failure

```css
html, body { overflow-x: clip; }
* , *::before, *::after { min-width: 0; }
img, svg, video, canvas { max-width: 100%; display: block; }
```

- Use `overflow-x: clip` on the root, never `overflow-x: hidden` on `body`
  alone (it creates a scroll container and breaks `position: sticky`).
- Every grid and flex child gets `min-width: 0` so long words cannot force the
  track wider than its container.
- Break long tokens: `overflow-wrap: anywhere` on code, URLs, and emails.
- Avoid `100vw` (it includes the scrollbar). Use `100%` or `100dvw`.
- Floating elements and pseudo-elements that stick out must be inside a
  container with `overflow: clip`.
- Decorative blurs and glows must live in an `overflow: hidden` wrapper.

### 4.2 Text wrapping

```css
h1, h2, h3, .display { text-wrap: balance; }
p, li, .prose { text-wrap: pretty; }
```

`balance` evens the line lengths in a headline. `pretty` stops orphans in body
copy. Together they remove the single most common "generated" tell.

### 4.3 Touch targets

```css
@media (pointer: coarse) {
  a, button, [role="button"], input, select, textarea {
    min-height: 44px;
    min-width: 44px;
  }
}
```

Visual size can stay small if the hit area is padded with a pseudo-element, but
the accessible hit area must be at least 44 by 44 CSS pixels.

### 4.4 Specificity discipline

- Never use `!important` outside the reduced-motion override.
- Keep component states at equal specificity and order them logically:
  base, hover, focus-visible, active, disabled.
- Scope page-level overrides to a class or a data attribute, never a bare
  element selector.
- Custom properties must be declared on `:root` (or `[data-theme]`) so any
  component can read them without importing anything.
- Logical properties everywhere: `margin-inline`, `padding-block`,
  `inset-inline-start`. The layout must survive RTL without a rewrite.

### 4.5 Layering order

Use an explicit cascade layer order so specificity fights stop:

```css
@layer reset, tokens, base, layout, components, utilities;
```

## 5. `prefers-reduced-motion` Rules

Mandatory, and the Phase 5 gate fails without it.

```css
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
  .step { opacity: 1; }
  .layer { transition: none; }
}
```

Beyond the CSS block, honor it in JS:

- `window.matchMedia('(prefers-reduced-motion: reduce)')` guards camera
  tweens: **instant cut** to the target `viewBox`, never a shorter tween.
- Listen for `change` on that media query and re-apply the current camera.
- Pause loops: marquees, marquee tickers, auto-playing moviescrollers, and
  canvas simulations must stop.
- Keep the information. Reduced motion is not reduced content: the scroll
  steps still activate, the layers still toggle, the data is still there.
- Never gate meaning behind motion. If a reveal carries the only copy, show the
  copy by default and reveal the enhancement.

## 6. Pre-Flight Self Audit

- Zero strings from section 1.1 anywhere in the source tree.
- `.studio/03-TOKENS.css` is linked or imported, not re-typed.
- Every section from the beat sheet exists, in order, with its documented
  archetype.
- Every `data-camera` and `data-layer` value resolves to a real `id`.
- Hover, focus-visible, active, disabled, empty, loading, and error states all
  exist for interactive and data-driven components.
- `prefers-reduced-motion` present in CSS and honored in JS.
- No horizontal overflow at 390px or 1440px.
- Touch targets at least 44 by 44 on coarse pointers.
- One `h1`, no skipped heading levels, landmarks present.

Then run:

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase 5 --dir .studio --target <entry-file-or-src-dir>
```

Quote the printed gate line verbatim. Only then move to Stage 6.
