# Spoke 02: Design Systems Architect (OKLCH Tokens & Anti-Slop)

**Load this file only when you are running Stage 3.**
Every rule here is enforced downstream by `verify_gate.py --phase 3` and
`--phase 5`, plus by the Blind Critic in Stage 6.

Stage 3 produces exactly one file: `.studio/03-TOKENS.css`. It must be
pasteable into a production project, not a mood swatch.

## 1. The Anti-Slop Ban List

Generic output is not a matter of taste, it is a set of tells. This list is the
punch list. Anything on it is a defect.

### 1.1 Banned font defaults

Never ship these as the primary system without a deliberate, documented display
counterpart: `Inter`, `Roboto`, `Open Sans`, `Lato`, `Helvetica`, `Arial`,
`system-ui` as a lazy fallback for a whole site.

They are not evil. They are invisible. When 90 percent of pages use them, using
them communicates nothing.

High-craft pairings, all freely available, all safe to use:

| Archetype | Display | Text | Notes |
| --- | --- | --- | --- |
| Editorial serif tech | Instrument Serif | Plus Jakarta Sans | high contrast serif, geometric sans |
| Fashion brutalist | Syne | DM Sans | wide grotesque display, quiet body |
| Warm craft | Fraunces | Cabinet Grotesk | soft optical serif, tight grotesque |
| Luxury lookbook | Playfair Display | Space Grotesk | didone display, technical body |
| Long-form reading | Newsreader | Geist | reading serif, neutral UI sans |
| Swiss precision | Archivo | Inter Tight | condensed authority, tight UI |
| Technical mono-first | JetBrains Mono | IBM Plex Sans | code-forward, neutral body |
| Soft product | Fraunces | Nunito Sans | friendly, high legibility |

Rules:

- Max **two** font families, plus an optional tabular mono for data and labels.
- Load at most 3 or 4 weights total. Weight variety is not personality.
- Display sizes need optical tracking: roughly `-0.02em` at hero size, `0em` at
  body size, `0.06em` on small caps labels.
- Set `font-variant-numeric: tabular-nums` anywhere numbers change in place.

### 1.2 Banned AI hex codes and color tells

| Banned | Why it is a tell | Use instead |
| --- | --- | --- |
| `#6366f1` | Tailwind indigo-500, the default AI gradient start | hue chosen from the brand |
| `#a855f7` | Tailwind purple-500, the default gradient end | hue chosen from the brand |
| `#8b5cf6` | Tailwind violet-500, the default glow | hue chosen from the brand |
| `#F4F1EA` with `#D97757` | the Claude terracotta tell | any non-default warm neutral |
| `#000000` on `#ffffff` | sterile, unconsidered | tinted surface, near-black ink |

Also banned as patterns, even with legal hexes:

- Purple-to-indigo linear gradients used as decoration on cards or headers.
- Neon glow on dark backgrounds with no functional purpose.
- Every surface a different hue. Surfaces differ by lightness, not by color.

### 1.3 Banned layout and copy tells

- Tracked-out ALL-CAPS eyebrow badges sitting above every single heading.
- Numbered `01 / 02 / 03` markers on content that is not sequential.
- Three identical rounded cards in a row with soft `rgba(0,0,0,0.1)` shadows.
- Cards nested inside cards.
- `->` or a right arrow appended to every CTA button.
- Exactly one word in every headline rendered italic or accent colored.
- Symmetric 50/50 split on every single section, forever.
- A hero that is always: centered headline, centered subhead, two centered
  buttons, and a centered screenshot.

## 2. Perceptual Single-Hue OKLCH Token Math

OKLCH is not a buzzword here. It is what makes a single hue produce a coherent
ramp: equal hue steps produce perceptually even lightness steps, so you can
derive an entire UI from two numbers.

### 2.1 The two seed hues

```css
:root {
  --brand-hue: 24;   /* the single brand hue, in oklch degrees */
  --accent-hue: 196; /* the single accent hue, deliberately far away */
}
```

### 2.2 The derivation recipe

Surfaces are **near-neutral**: low chroma, high lightness, brand hue carried at
low saturation so the page never looks color-cast.

| Token | Formula | Notes |
| --- | --- | --- |
| `--surface-bg` | `oklch(0.985 0.004 var(--brand-hue))` | paper, never pure white |
| `--surface-elevated` | `oklch(1 0 0)` or `oklch(0.995 0.003 var(--brand-hue))` | cards lifted off the bg |
| `--surface-sunken` | `oklch(0.955 0.008 var(--brand-hue))` | wells, code blocks, insets |
| `--surface-glass` | `oklch(1 0 0 / 0.62)` plus backdrop blur | nav over media |
| `--surface-border` | `oklch(0.88 0.010 var(--brand-hue))` | hairlines, 1px only |
| `--ink-primary` | `oklch(0.21 0.018 var(--brand-hue))` | body and headings |
| `--ink-secondary` | `oklch(0.44 0.016 var(--brand-hue))` | secondary copy |
| `--ink-muted` | `oklch(0.58 0.012 var(--brand-hue))` | captions, axis labels |
| `--ink-accent` | `oklch(0.58 0.17 var(--accent-hue))` | the only saturated color |

Dark mode is a **lightness inversion**, not a new palette. Keep both hues,
swap the L axis, and drop chroma so dark surfaces do not glow:

```css
@media (prefers-color-scheme: dark) {
  :root {
    --surface-bg: oklch(0.17 0.012 var(--brand-hue));
    --surface-elevated: oklch(0.21 0.014 var(--brand-hue));
    --surface-sunken: oklch(0.14 0.012 var(--brand-hue));
    --surface-glass: oklch(0.21 0.014 var(--brand-hue) / 0.66);
    --surface-border: oklch(0.32 0.016 var(--brand-hue));
    --ink-primary: oklch(0.96 0.006 var(--brand-hue));
    --ink-secondary: oklch(0.78 0.012 var(--brand-hue));
    --ink-muted: oklch(0.62 0.012 var(--brand-hue));
    --ink-accent: oklch(0.74 0.15 var(--accent-hue));
  }
}
```

### 2.3 The 60-30-10 rule and contrast floors

- **60** surface, **30** ink and neutral surfaces, **10** accent. If accent
  covers more than roughly a tenth of the visible page, the hierarchy collapses.
- Body text at `oklch(0.21 ...)` on `oklch(0.985 ...)` lands well above the
  **WCAG 4.5:1** AA floor. Verify any pair you introduce.
- Large display type (24px and up, or 19px bold and up) needs **3:1**.
- `--ink-muted` is for non-essential text only. If it carries meaning, it must
  still clear 4.5:1.
- Focus rings use `--ink-accent` at 2px with a 2px offset, never `outline: none`.

## 3. Fluid Typography

One rule drives the whole scale: **fluid clamp between a mobile floor and a
desktop ceiling, with a comfortable middle.**

```css
--text-hero: clamp(2.75rem, 1.10rem + 7.2vw, 7.5rem);
--text-h1:   clamp(2.25rem, 1.35rem + 3.9vw, 4.25rem);
--text-h2:   clamp(1.75rem, 1.25rem + 2.2vw, 2.75rem);
--text-h3:   clamp(1.25rem, 1.05rem + 0.9vw, 1.65rem);
--text-body: clamp(1rem, 0.94rem + 0.28vw, 1.125rem);
--text-mono: clamp(0.8125rem, 0.78rem + 0.16vw, 0.9rem);
```

Typography rules that survive contact with a real page:

- Body line-height 1.55 to 1.7. Hero line-height 0.92 to 1.05, tight.
- Measure 60 to 75 characters (`max-width: 65ch`) for prose.
- `text-wrap: balance` on every heading, `text-wrap: pretty` on paragraphs.
- Tabular numerals on any metric, price, timestamp, or counter.
- Never scale type below 12px. Captions live at 13 to 14px.

## 4. Spacing, Radius, Elevation, Easing

Spacing is a 4px/8px grid. Name the steps, then use the names everywhere:

```css
--space-1: 0.25rem;  /* 4  */
--space-2: 0.5rem;   /* 8  */
--space-3: 0.75rem;  /* 12 */
--space-4: 1rem;     /* 16 */
--space-5: 1.5rem;   /* 24 */
--space-6: 2rem;     /* 32 */
--space-7: 3rem;     /* 48 */
--space-8: 4rem;     /* 64 */
--space-9: 6rem;     /* 96 */
--space-10: 8rem;    /* 128 */
```

- Radius scale: `--radius-sm: 4px`, `--radius-md: 10px`, `--radius-lg: 18px`,
  `--radius-pill: 999px`. Pick **one** per surface class and repeat it.
- Elevation in OKLCH with a hint of the brand hue, never pure black:
  `--shadow-1: 0 1px 2px oklch(0.21 0.018 var(--brand-hue) / 0.06)`,
  `--shadow-2: 0 8px 24px oklch(0.21 0.018 var(--brand-hue) / 0.10)`.
  Borders over shadows. Shadows over gradients.
- Easing tokens, five total, used everywhere:

```css
--ease-out:    cubic-bezier(0.22, 1, 0.36, 1);
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
--ease-snap:   cubic-bezier(0.16, 1, 0.3, 1);
--ease-linear: linear;
```

Durations: micro 120ms, control 200ms, section 480ms, camera 900ms. Anything
scrubbed by scroll uses `--ease-out` only.

## 5. Kinetic Typography & Variable Font Physics

Display type is a physical body, not a picture of one. When a variable font
exposes `wght` and `wdth`, you can bind scroll velocity to optical weight and
skew, and the headline gains mass without a single extra keyframe.

### 5.1 The velocity token

`--scroll-velocity` is a signed unitless value, roughly `-1` to `1`, published
from JS on every scroll frame and eased down so it decays instead of
stuttering:

```css
@property --scroll-velocity {
  syntax: "<number>";
  inherits: true;
  initial-value: 0;
}

:root {
  --scroll-velocity: 0;
  --weight-dynamic: 500;
  --width-dynamic: 100;
}
```

Publish it with a decaying lerp, never a raw delta, or the skew jitters:

```js
let lastY = window.scrollY;
let velocity = 0;
let ticking = false;

function publishVelocity() {
  const y = window.scrollY;
  const delta = y - lastY;
  lastY = y;
  const instant = Math.max(-1, Math.min(1, delta / 60));
  velocity += (instant - velocity) * 0.18;
  document.documentElement.style.setProperty(
    '--scroll-velocity',
    velocity.toFixed(4)
  );
  ticking = false;
}

window.addEventListener(
  'scroll',
  () => {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(publishVelocity);
  },
  { passive: true }
);
```

### 5.2 Binding velocity to optical weight and skew

The skew clamp is the whole trick. Four degrees is the ceiling; past that the
type stops looking like type and starts looking like a bug:

```css
.kinetic-display {
  font-variation-settings:
    "wght" calc(var(--weight-dynamic) + (var(--scroll-velocity) * 120))
    "wdth" calc(var(--width-dynamic) + (var(--scroll-velocity) * 6));
  transform: skewY(
    clamp(-4deg, calc(var(--scroll-velocity) * 0.15deg), 4deg)
  );
  transform-origin: 0 100%;
  transition: transform 120ms var(--ease-out);
}
```

Bounded by construction: `clamp()` guarantees the output never leaves
`-4deg..4deg` no matter how violent the scroll, so the effect can never
produce unreadable or overflow-inducing geometry.

### 5.3 Split-line mask reveals

Each line is a clipped band and its inner content slides up from below. This
beats a fade because the type appears to have been *there* and been uncovered:

```css
.line-mask {
  display: block;
  overflow: clip;
  padding-block: 0.08em;
}

.line-inner {
  display: block;
  transform: translateY(105%);
  transition: transform 720ms var(--ease-out);
}

.is-revealed .line-inner {
  transform: translateY(0);
}

.line-inner:nth-child(2) { transition-delay: 80ms; }
.line-inner:nth-child(3) { transition-delay: 160ms; }
```

```html
<h1 class="kinetic-display">
  <span class="line-mask"><span class="line-inner">A request leaves</span></span>
  <span class="line-mask"><span class="line-inner">the edge in 4&nbsp;ms</span></span>
</h1>
```

Use `overflow: clip`, never `overflow: hidden`: `hidden` creates a scroll
container and breaks `position: sticky` on any ancestor.

### 5.4 Reduced motion is a cut, not a shorter slide

```css
@media (prefers-reduced-motion: reduce) {
  .kinetic-display { transform: none; font-variation-settings: normal; }
  .line-inner { transform: none; transition: none; }
}
```

Leave the words visible. Reduced motion must never remove content, only the
travel.

## 6. Template: `.studio/03-TOKENS.css`

The gate requires `:root`, `oklch(`, `clamp(`, and `--font-`, a minimum of 250
characters, and zero banned hex codes. This template satisfies all of them.

```css
/* 03 TOKENS - perceptual single-hue OKLCH system
   Derived from --brand-hue and --accent-hue. No hardcoded AI hex codes. */

:root {
  color-scheme: light dark;

  /* --- hue seeds ------------------------------------------------------ */
  --brand-hue: 24;
  --accent-hue: 196;

  /* --- surfaces (60%) ------------------------------------------------- */
  --surface-bg: oklch(0.985 0.004 var(--brand-hue));
  --surface-elevated: oklch(1 0 0);
  --surface-sunken: oklch(0.955 0.008 var(--brand-hue));
  --surface-glass: oklch(1 0 0 / 0.62);
  --surface-border: oklch(0.88 0.010 var(--brand-hue));

  /* --- ink (30%) ------------------------------------------------------ */
  --ink-primary: oklch(0.21 0.018 var(--brand-hue));
  --ink-secondary: oklch(0.44 0.016 var(--brand-hue));
  --ink-muted: oklch(0.58 0.012 var(--brand-hue));
  --ink-inverse: oklch(0.99 0.004 var(--brand-hue));

  /* --- accent (10%) ---------------------------------------------------- */
  --ink-accent: oklch(0.58 0.17 var(--accent-hue));
  --ink-accent-hover: oklch(0.50 0.17 var(--accent-hue));
  --accent-wash: oklch(0.95 0.045 var(--accent-hue));
  --accent-ink: oklch(0.30 0.09 var(--accent-hue));

  /* --- status ---------------------------------------------------------- */
  --ok: oklch(0.62 0.15 148);
  --warn: oklch(0.72 0.15 76);
  --danger: oklch(0.55 0.19 27);

  /* --- typography ------------------------------------------------------ */
  --font-display: "Instrument Serif", "Iowan Old Style", Georgia, serif;
  --font-body: "Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", monospace;

  --text-hero: clamp(2.75rem, 1.10rem + 7.2vw, 7.5rem);
  --text-h1: clamp(2.25rem, 1.35rem + 3.9vw, 4.25rem);
  --text-h2: clamp(1.75rem, 1.25rem + 2.2vw, 2.75rem);
  --text-h3: clamp(1.25rem, 1.05rem + 0.9vw, 1.65rem);
  --text-body: clamp(1rem, 0.94rem + 0.28vw, 1.125rem);
  --text-mono: clamp(0.8125rem, 0.78rem + 0.16vw, 0.9rem);

  --leading-tight: 1.02;
  --leading-snug: 1.25;
  --leading-body: 1.62;
  --tracking-display: -0.02em;
  --tracking-label: 0.08em;
  --measure: 65ch;

  /* --- spacing: 4px / 8px grid ----------------------------------------- */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.5rem;
  --space-6: 2rem;
  --space-7: 3rem;
  --space-8: 4rem;
  --space-9: 6rem;
  --space-10: 8rem;

  /* --- radius, elevation, motion --------------------------------------- */
  --radius-sm: 4px;
  --radius-md: 10px;
  --radius-lg: 18px;
  --radius-pill: 999px;

  --shadow-1: 0 1px 2px oklch(0.21 0.018 var(--brand-hue) / 0.06);
  --shadow-2: 0 8px 24px oklch(0.21 0.018 var(--brand-hue) / 0.10);
  --shadow-3: 0 24px 60px oklch(0.21 0.018 var(--brand-hue) / 0.14);

  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-snap: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-linear: linear;

  --dur-micro: 120ms;
  --dur-control: 200ms;
  --dur-section: 480ms;
  --dur-camera: 900ms;
}

/* Manual theme override for a visible light/dark toggle. */
[data-theme="dark"] {
  --surface-bg: oklch(0.17 0.012 var(--brand-hue));
  --surface-elevated: oklch(0.21 0.014 var(--brand-hue));
  --surface-sunken: oklch(0.14 0.012 var(--brand-hue));
  --surface-glass: oklch(0.21 0.014 var(--brand-hue) / 0.66);
  --surface-border: oklch(0.32 0.016 var(--brand-hue));
  --ink-primary: oklch(0.96 0.006 var(--brand-hue));
  --ink-secondary: oklch(0.78 0.012 var(--brand-hue));
  --ink-muted: oklch(0.62 0.012 var(--brand-hue));
  --ink-inverse: oklch(0.17 0.012 var(--brand-hue));
  --ink-accent: oklch(0.74 0.15 var(--accent-hue));
  --ink-accent-hover: oklch(0.82 0.13 var(--accent-hue));
  --accent-wash: oklch(0.28 0.05 var(--accent-hue));
  --accent-ink: oklch(0.92 0.06 var(--accent-hue));
  --shadow-1: 0 1px 2px oklch(0 0 0 / 0.40);
  --shadow-2: 0 8px 24px oklch(0 0 0 / 0.48);
  --shadow-3: 0 24px 60px oklch(0 0 0 / 0.56);
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --surface-bg: oklch(0.17 0.012 var(--brand-hue));
    --surface-elevated: oklch(0.21 0.014 var(--brand-hue));
    --surface-sunken: oklch(0.14 0.012 var(--brand-hue));
    --surface-glass: oklch(0.21 0.014 var(--brand-hue) / 0.66);
    --surface-border: oklch(0.32 0.016 var(--brand-hue));
    --ink-primary: oklch(0.96 0.006 var(--brand-hue));
    --ink-secondary: oklch(0.78 0.012 var(--brand-hue));
    --ink-muted: oklch(0.62 0.012 var(--brand-hue));
    --ink-inverse: oklch(0.17 0.012 var(--brand-hue));
    --ink-accent: oklch(0.74 0.15 var(--accent-hue));
  }
}
```

Tailwind v4 equivalent (paste into your CSS entry, not into this file):

```css
@import "tailwindcss";

@theme {
  --color-surface: oklch(0.985 0.004 24);
  --color-surface-elevated: oklch(1 0 0);
  --color-ink: oklch(0.21 0.018 24);
  --color-ink-muted: oklch(0.58 0.012 24);
  --color-accent: oklch(0.58 0.17 196);
  --font-display: "Instrument Serif", Georgia, serif;
  --font-body: "Plus Jakarta Sans", ui-sans-serif, system-ui, sans-serif;
  --text-hero: clamp(2.75rem, 1.10rem + 7.2vw, 7.5rem);
  --text-body: clamp(1rem, 0.94rem + 0.28vw, 1.125rem);
  --spacing-4: 1rem;
  --spacing-8: 2rem;
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
}
```

## 7. Pre-Flight Self Audit

Run this list before invoking the gate:

- No `#6366f1`, `#a855f7`, `#8b5cf6`, no purple-indigo decorative gradient.
- Two font families maximum, plus optional tabular mono.
- Every color is `oklch()` and traces to `--brand-hue` or `--accent-hue`.
- Accent appears on roughly a tenth of the surface, no more.
- Body text clears WCAG 4.5:1, large text clears 3:1.
- Every type size is a `clamp()` with a sane floor and ceiling.
- All spacing comes from the `--space-*` scale.
- At least one real focus-visible style exists in the tokens' consumers.

Then run:

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase 3 --dir .studio
```

Quote the printed gate line verbatim.
