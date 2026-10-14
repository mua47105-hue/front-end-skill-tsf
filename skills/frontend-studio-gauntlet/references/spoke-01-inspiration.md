# Spoke 01: Visual Researcher (Inspiration & Named Quality Bar)

**Load this file only when you are running Stage 2.**
Do not preload it. Do not quote rules from it during other stages.

Your job in Stage 2 is to arrive at a **Named Quality Bar** that is real,
fetchable, and comparable. You are not collecting "inspiration vibes". You are
pinning a measurable finish line that Stage 6 will hold your render against.

## 1. The Research Bench

Seven platforms, each with a distinct job. Use at least four of them.

| Platform | URL | Best for | Do not use it for |
| --- | --- | --- | --- |
| Pinterest | https://www.pinterest.com | Mass art direction, moodboards, texture and prop references, type pairing photos | Final UX verification, or copy you intend to ship |
| Awwwards | https://www.awwwards.com | Top-tier interaction craft, motion signatures, portfolio-grade art direction | Generic SaaS landing pages, it overfits to the agency look |
| Godly | https://godly.website | Tasteful minimal and typographic marketing sites, whitespace discipline | Dense or playful brands |
| Mobbin | https://mobbin.com | Real product UI patterns: dashboards, settings, empty states, mobile flows | Expressive brand moments and hero art direction |
| The Pudding | https://pudding.cool | Scrollytelling and data journalism mechanics, annotation patterns, narrative pacing | Consumer marketing pages |
| Land-book | https://land-book.com | Site-level inspiration: hero composition, header behavior, footer density | Interaction detail, it is mostly stills |
| Design Spells | https://www.designspells.com | Specific delightful micro-interactions you can re-implement in an hour | Overall visual direction |

Research protocol:

1. Pick the archetype from Stage 1 and run the matching Pinterest operator below.
2. Sweep Godly and Land-book for **section composition**, not color.
3. Sweep Mobbin for the product-surface patterns your pages will need.
4. Sweep The Pudding if Stage 1 set `MOTION_INTENSITY >= 5`.
5. Pick two or three candidates and actually open them. Screenshot the hero at
   1440px. If you cannot fetch the URL, it is not a bar.

## 2. Pinterest Art Direction Operators

Use these verbatim as search strings. They encode the archetype from Stage 1.

**Swiss / Editorial Grid**

```text
site:pinterest.com "swiss graphic design" OR "editorial web layout" typography grid
```

**Industrial / Tactile Hardware UI**

```text
site:pinterest.com "teenage engineering UI" OR "braun industrial interface" web design
```

**Luxury / High-Craft Lookbook**

```text
site:pinterest.com "art direction web design" serif lookbook layout
```

**Scrollytelling & Data Journalism**

```text
site:pinterest.com "information design" OR "scrollytelling" interactive infographic
```

**Dark Precision / Developer Cockpit**

```text
site:pinterest.com "dark mode UI" bento grid precision typography
```

Pair each Pinterest search with a real site sweep on Awwwards and Godly using
the same three keywords. Pinterest supplies the mood, the site sweep supplies
the mechanics you must reproduce.

## 3. The 3 Rules of a Valid Gauntlet Quality Bar

1. **Named.** It has a title you can type in one line: "Stripe Sessions 2024
   hero", "NYT Snow Fall pinned map stage", "Teenage Engineering OP-1 field
   manual". "Some cool site" is not a bar.
2. **Fetchable.** You have a working URL you opened in this session, plus a
   1440px screenshot you can look at again during Stage 6. If the URL 404s or
   is behind a wall, it is disqualified.
3. **Comparable.** You can put your render and the reference side by side on
   the same axes (hero focal point, section rhythm, typographic tension, finish
   quality) and reach a verdict. A reference that is 3D art and your page is a
   dashboard is not comparable; pick a reference that solves the same problem.

Two or three references is the target. One is a mood, not a bar. Five is noise.

## 4. Anti-Patterns for This Stage

- **Screenshot graveyard**: 40 pins, zero decisions. Cap the moodboard at 3
  bars plus notes.
- **Unfetchable flex**: a Behance concept with no live build. Not fetchable.
- **Averaging**: three references that disagree on density. Pick a primary bar
  and a secondary bar with one explicit difference.
- **Copying identity**: do not lift logos, product names, or illustration.
  Steal mechanics: the hero ratio, the grid, the pacing, the type behavior.

## 5. Template: `.studio/02-MOODBOARD.md`

The Phase 2 gate requires the headings `Primary Bar`, `Hero Treatment`,
`Grid & Section Rhythm`, and `Typography Behavior`, plus at least one real
`https://` URL and 300 characters minimum. Use exactly this shape.

```markdown
# 02 Moodboard & Named Quality Bar

Project: <one line restating the Stage 1 job-to-be-done>
Archetype: <the Stage 1 aesthetic archetype>
Motion Intensity: <integer 1-10 from Stage 1>

## Primary Bar

- Name: <specific title of the reference>
- URL: https://<working-url-opened-this-session>
- Screenshot: <path or note where the 1440px capture lives>
- Why comparable: <one sentence, same problem as our page>
- What we steal: <2-3 concrete mechanics>

## Secondary Bar

- Name: <specific title of the reference>
- URL: https://<working-url-opened-this-session>
- Screenshot: <path or note where the 1440px capture lives>
- How it differs from the Primary Bar: <exactly one axis, e.g. denser, colder>
- What we steal: <1-2 concrete mechanics>

## Hero Treatment

- Focal point: <the single thing the eye lands on in the first 300ms>
- Aspect and crop: <e.g. full-bleed 21:9 photo, 4:5 portrait crop>
- Type over media: <placement, size relative to viewport, alignment>
- Depth cues: <overlay, vignette, grain, shadow, none>

## Grid & Section Rhythm

- Column system: <e.g. 12-col with 5/7 asymmetric splits>
- Section cadence: <the alternation sequence, e.g. contained, full-bleed, split>
- Density map: <where the page breathes and where it crowds>
- Repetition ban: <what must never appear twice in a row>

## Typography Behavior

- Display face: <family, weight, optical size, tracking at display sizes>
- Text face: <family, weight, measure in characters>
- Scale behavior: <how the type fluidly resizes between 390px and 1440px>
- Numerals and mono: <tabular or not, where mono is used>

## Color & Surface Texture

- Surface strategy: <flat, tinted, glass, paper, grain>
- Accent discipline: <where the single accent hue is allowed to appear>
- Contrast targets: <body text ratio, muted text ratio>

## Image & Media Art Direction

- Subject matter: <what is photographed or illustrated>
- Treatment: <duotone, monochrome, natural, product-on-plinth>
- Media mix: <photography, illustration, 3D, type-only, data marks>
- Motion in media: <parallax, ken burns, none>
```

## 6. Handoff to Stage 3

Before running the gate, confirm:

- Every reference name is specific enough to say out loud.
- Every URL was opened in this session and returned a real page.
- The Primary Bar and Secondary Bar differ on exactly one documented axis.
- The `Typography Behavior` and `Color & Surface Texture` sections describe
  something Stage 3 can turn into `oklch()` tokens and `clamp()` sizes.

Then run:

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase 2 --dir .studio
```

Quote the printed gate line verbatim in your report. Do not advance on a claim.
