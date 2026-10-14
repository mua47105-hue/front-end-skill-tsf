#!/usr/bin/env node
/**
 * playwright_gauntlet.js - automated Stage 6 browser gauntlet.
 *
 * Launches headless Chromium twice (Desktop 1440x900 and Mobile 390x844) and
 * proves the runtime is clean:
 *
 *   - 0 console.error entries and 0 uncaught page errors
 *   - 0 broken images (every <img> is complete with naturalWidth > 0)
 *   - 0 horizontal overflow (documentElement.scrollWidth <= window.innerWidth)
 *   - 100% [data-step] activation while scrolling the page
 *
 * Saves desktop-1440x900.png and mobile-390x844.png plus report.json into the
 * --out directory, prints a human summary and a JSON block, and exits 1 when
 * any check failed.
 *
 * Written as CommonJS with universal "node:" built-ins so it runs whether the
 * surrounding project is CommonJS or ESM, and so skill zip uploaders that
 * classify by MIME type recognize this file as text/javascript rather than
 * application/octet-stream (which is what a .mjs extension resolves to).
 *
 * Usage:
 *   node playwright_gauntlet.js --url ./index.html --out .studio/screenshots
 *   node playwright_gauntlet.js --url https://example.com --out ./shots --timeout 30000
 *
 * Options:
 *   --url <http-url-or-local-path>  target to test (required)
 *   --out <dir>                     screenshot output directory (default .studio/screenshots)
 *   --timeout <ms>                  per-viewport navigation budget (default 30000)
 *   --settle <ms>                   post-scroll settle time for step activation (default 450)
 *   --viewport-only                 capture the viewport instead of the full page
 *   --headed                        run with a visible browser (debugging only)
 */

"use strict";

const { existsSync } = require("node:fs");
const { mkdir, writeFile } = require("node:fs/promises");
const { createRequire } = require("node:module");
const path = require("node:path");
const process = require("node:process");
const { pathToFileURL } = require("node:url");

const VIEWPORTS = [
  {
    label: "desktop",
    width: 1440,
    height: 900,
    deviceScaleFactor: 1,
    isMobile: false,
    hasTouch: false,
    userAgent:
      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
  },
  {
    label: "mobile",
    width: 390,
    height: 844,
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
    userAgent:
      "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
  },
];

const INSTALL_HINT = [
  "Playwright is not installed, so the browser gauntlet cannot run.",
  "",
  "Install it in the project under test:",
  "  npm init -y",
  "  npm install -D playwright",
  "  npx playwright install chromium",
  "",
  "On a headless Linux box also install the OS libraries:",
  "  npx playwright install --with-deps chromium",
  "",
  "Or drive an already-running browser through the Playwright MCP server.",
  "Until a real browser run happens, Stage 6 is BLOCKED, never WIN.",
].join("\n");

function fail(message) {
  process.stderr.write(`${message}\n`);
  process.exit(2);
}

function printHelp() {
  process.stdout.write(
    [
      "playwright_gauntlet.js - Stage 6 browser gauntlet",
      "",
      "Usage:",
      "  node playwright_gauntlet.js --url <http-url-or-local-path> [--out <dir>]",
      "",
      "Options:",
      "  --url <url|path>     target to test (required)",
      "  --out <dir>          screenshot directory (default: .studio/screenshots)",
      "  --timeout <ms>       navigation budget per viewport (default: 30000)",
      "  --settle <ms>        settle time after each scroll (default: 450)",
      "  --viewport-only      capture the viewport instead of the full page",
      "  --headed             run with a visible browser",
      "  -h, --help           show this help",
      "",
      "Exit codes: 0 all checks passed, 1 a check failed, 2 could not run.",
      "",
    ].join("\n")
  );
}

function parseArgs(argv) {
  const options = {
    url: null,
    out: ".studio/screenshots",
    timeout: 30000,
    settle: 450,
    fullPage: true,
    headed: false,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "-h" || arg === "--help") {
      printHelp();
      process.exit(0);
    }
    if (!arg.startsWith("--")) {
      if (!options.url) {
        options.url = arg;
        continue;
      }
      fail(`Unexpected positional argument: ${arg}`);
    }

    const equals = arg.indexOf("=");
    const key = equals === -1 ? arg.slice(2) : arg.slice(2, equals);
    const inlineValue = equals === -1 ? null : arg.slice(equals + 1);
    const takeValue = () => {
      if (inlineValue !== null) return inlineValue;
      index += 1;
      if (index >= argv.length) fail(`Option --${key} requires a value.`);
      return argv[index];
    };

    switch (key) {
      case "url":
        options.url = takeValue();
        break;
      case "out":
        options.out = takeValue();
        break;
      case "timeout":
        options.timeout = Number(takeValue());
        break;
      case "settle":
        options.settle = Number(takeValue());
        break;
      case "viewport-only":
        options.fullPage = false;
        break;
      case "headed":
        options.headed = true;
        break;
      default:
        fail(`Unknown option: --${key} (try --help)`);
    }
  }

  if (!options.url) fail("Missing required --url. Try --help.");
  if (!Number.isFinite(options.timeout) || options.timeout <= 0) {
    fail("--timeout must be a positive number of milliseconds.");
  }
  if (!Number.isFinite(options.settle) || options.settle < 0) {
    fail("--settle must be a positive number of milliseconds.");
  }
  return options;
}

/**
 * Resolve and load Playwright.
 *
 * A bare "playwright" specifier resolves relative to *this script*, which
 * lives inside the skill directory, not the project under test. The project
 * is where Playwright is installed, so every candidate resolution root is
 * tried explicitly, starting with the target project.
 */
async function loadPlaywright() {
  const roots = [
    process.cwd(),
    path.join(process.cwd(), "node_modules"),
    __dirname,
    path.join(__dirname, "..", "node_modules"),
    path.join(__dirname, "..", "..", "..", "node_modules"),
  ].filter((root) => {
    try {
      return existsSync(root);
    } catch {
      return false;
    }
  });

  // 1. CommonJS load resolved from each root.
  for (const root of roots) {
    try {
      const scoped = createRequire(path.join(root, "gauntlet-resolution-anchor.js"));
      const resolved = scoped.resolve("playwright");
      const loaded = scoped(resolved);
      if (loaded && loaded.chromium) return loaded;
    } catch {
      // try the next root
    }
  }

  // 2. ESM-only build of Playwright, still resolved from the target project.
  for (const root of roots) {
    try {
      const scoped = createRequire(path.join(root, "gauntlet-resolution-anchor.js"));
      const resolved = scoped.resolve("playwright");
      const loaded = await import(pathToFileURL(resolved).href);
      if (loaded && loaded.chromium) return loaded;
    } catch {
      // try the next root
    }
  }

  // 3. Last resort: a plain dynamic import from the ambient resolution path.
  try {
    const mod = await import("playwright");
    if (mod && mod.chromium) return mod;
  } catch {
    // fall through to the install hint
  }

  return null;
}

function resolveTarget(rawUrl) {
  if (/^https?:\/\//i.test(rawUrl)) return { url: rawUrl, kind: "remote" };
  const absolute = path.resolve(process.cwd(), rawUrl);
  if (!existsSync(absolute)) {
    fail(`No such file or directory: ${absolute}`);
  }
  if (absolute.endsWith(".html") || absolute.endsWith(".htm")) {
    return { url: pathToFileURL(absolute).href, kind: "local-file" };
  }
  const indexFile = path.join(absolute, "index.html");
  if (existsSync(indexFile)) {
    return { url: pathToFileURL(indexFile).href, kind: "local-dir" };
  }
  fail(`No HTML entry point found for '${rawUrl}'. Serve the directory or pass a file.`);
  return null;
}

async function collectMetrics(page) {
  return page.evaluate(() => {
    const doc = document.documentElement;
    const images = Array.from(document.images);
    const broken = images
      .filter((img) => !(img.complete && img.naturalWidth > 0))
      .map((img) => img.currentSrc || img.src || "(no src)");

    let widest = null;
    const limit = doc.clientWidth;
    for (const el of document.querySelectorAll("body *")) {
      const rect = el.getBoundingClientRect();
      if (rect.width === 0 && rect.height === 0) continue;
      if (rect.right > limit + 1 || rect.left < -1) {
        widest = widest && widest.right >= rect.right
          ? widest
          : {
              tag: el.tagName.toLowerCase(),
              id: el.id || "",
              className: (el.getAttribute("class") || "").slice(0, 80),
              left: Math.round(rect.left),
              right: Math.round(rect.right),
            };
      }
    }

    let reducedMotionRules = 0;
    for (const sheet of Array.from(document.styleSheets)) {
      let rules;
      try {
        rules = sheet.cssRules;
      } catch {
        continue;
      }
      for (const rule of Array.from(rules || [])) {
        const texts = [rule.conditionText, rule.media ? rule.media.mediaText : ""];
        for (const nested of Array.from(rule.cssRules || [])) {
          texts.push(nested.conditionText);
        }
        for (const text of texts) {
          if (text && text.indexOf("prefers-reduced-motion") !== -1) reducedMotionRules += 1;
        }
      }
    }

    return {
      title: document.title,
      innerWidth: window.innerWidth,
      innerHeight: window.innerHeight,
      scrollWidth: doc.scrollWidth,
      clientWidth: doc.clientWidth,
      pageHeight: doc.scrollHeight,
      imageCount: images.length,
      brokenImages: broken,
      stepCount: document.querySelectorAll("[data-step]").length,
      interactiveHeroCount: document.querySelectorAll("[data-interactive-hero]").length,
      spellCount: document.querySelectorAll("[data-spell]").length,
      spellNames: Array.from(
        new Set(
          Array.from(document.querySelectorAll("[data-spell]"))
            .map((node) => node.getAttribute("data-spell"))
            .filter(Boolean)
        )
      ),
      overflowOffender: widest,
      reducedMotionRules,
    };
  });
}

function readStepState(page, index) {
  return page.evaluate((stepIndex) => {
    const element = document.querySelectorAll("[data-step]")[stepIndex];
    if (!element) return null;
    const classes = Array.from(element.classList);
    const activeClasses = classes.filter(
      (name) =>
        name === "active" ||
        name === "is-active" ||
        name.endsWith("-active") ||
        name.startsWith("active")
    );
    const active =
      element.getAttribute("data-active") === "true" ||
      element.getAttribute("aria-current") === "true" ||
      element.getAttribute("data-state") === "active" ||
      activeClasses.length > 0;
    return {
      id: element.id || element.getAttribute("data-step") || `step-${stepIndex + 1}`,
      active,
      activeClasses,
      classes,
      dataActive: element.getAttribute("data-active"),
      camera: element.getAttribute("data-camera"),
      layers: element.getAttribute("data-layer"),
    };
  }, index);
}

async function scrollStepIntoBand(page, index) {
  return page.evaluate((stepIndex) => {
    const element = document.querySelectorAll("[data-step]")[stepIndex];
    if (!element) return null;

    // A page that sets `html { scroll-behavior: smooth }` makes
    // window.scrollTo({ behavior: "auto" }) animate anyway, because "auto"
    // inherits the computed value from the scrolling box. A long jump (>= 1
    // viewport) would still be in flight when the settle timer expires, and
    // the step would read as inactive. Force the computed behavior to instant
    // for the duration of the jump, then restore it.
    const root = document.documentElement;
    const previousBehavior = root.style.scrollBehavior;
    root.style.scrollBehavior = "auto";

    const rect = element.getBoundingClientRect();
    const desired = rect.top - window.innerHeight * 0.4;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const next = Math.max(0, Math.min(window.scrollY + desired, max));
    window.scrollTo({ top: next, left: 0, behavior: "instant" });

    root.style.scrollBehavior = previousBehavior;

    return {
      id: element.id || element.getAttribute("data-step") || `step-${stepIndex + 1}`,
      scrollY: window.scrollY,
      target: next,
    };
  }, index);
}

async function resetScrollToTop(page) {
  await page.evaluate(() => {
    const root = document.documentElement;
    const previousBehavior = root.style.scrollBehavior;
    root.style.scrollBehavior = "auto";
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
    root.style.scrollBehavior = previousBehavior;
  });
  await page.waitForTimeout(150);
}

/**
 * Drive the first [data-interactive-hero] with synthetic pointer and click
 * events and prove that doing so raises no new console or page errors.
 *
 * A hero instrument that only works until you touch it is a broken hero, and
 * a shader or spring rig wired to a pointer is exactly where that failure
 * hides: uninitialised contexts, undefined uniforms, null refs on the first
 * move.
 */
async function interactWithHero(page, consoleErrors, pageErrors) {
  const before = { consoleErrors: consoleErrors.length, pageErrors: pageErrors.length };

  const target = await page.evaluate(() => {
    const hero = document.querySelector("[data-interactive-hero]");
    if (!hero) return null;
    hero.scrollIntoView({ block: "center", behavior: "instant" });
    const rect = hero.getBoundingClientRect();
    return {
      tag: hero.tagName.toLowerCase(),
      id: hero.id || "",
      spells: Array.from(hero.querySelectorAll("[data-spell]")).map((n) =>
        n.getAttribute("data-spell")
      ),
      box: {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2,
        width: rect.width,
        height: rect.height,
      },
    };
  });

  if (!target) {
    return { found: false, passed: true, detail: "no [data-interactive-hero] on this page" };
  }

  await page.waitForTimeout(120);
  await page.mouse.move(target.box.x, target.box.y);
  await page.mouse.move(target.box.x - 40, target.box.y - 24, { steps: 6 });
  await page.mouse.move(target.box.x + 32, target.box.y + 18, { steps: 6 });
  await page.waitForTimeout(150);

  // pointerenter plus an explicit click, dispatched in-page so listeners bound
  // to either the hero or an inner control are both exercised.
  const dispatched = await page.evaluate(() => {
    const hero = document.querySelector("[data-interactive-hero]");
    if (!hero) return 0;
    const rect = hero.getBoundingClientRect();
    const init = {
      bubbles: true,
      cancelable: true,
      clientX: rect.left + rect.width / 2,
      clientY: rect.top + rect.height / 2,
      pointerId: 1,
      pointerType: "mouse",
      isPrimary: true,
    };
    hero.dispatchEvent(new PointerEvent("pointerenter", init));
    hero.dispatchEvent(new PointerEvent("pointermove", init));
    const control = hero.matches("button, a, [role='button']")
      ? hero
      : hero.querySelector("button, a, [role='button']");
    if (control) control.dispatchEvent(new MouseEvent("click", init));
    return control ? 1 : 0;
  });

  await page.waitForTimeout(250);

  const newConsoleErrors = consoleErrors.length - before.consoleErrors;
  const newPageErrors = pageErrors.length - before.pageErrors;
  const clean = newConsoleErrors === 0 && newPageErrors === 0;

  const parts = [
    `hero <${target.tag}${target.id ? ` id="${target.id}"` : ""}>`,
    `${target.spells.length} spell(s) inside the hero`,
    `click dispatched: ${dispatched ? "yes" : "no"}`,
    `+${newConsoleErrors} console.error, +${newPageErrors} pageerror`,
  ];

  return {
    found: true,
    passed: clean,
    newConsoleErrors,
    newPageErrors,
    spellsInHero: target.spells,
    detail: parts.join(", "),
  };
}

/**
 * Sample 20 requestAnimationFrame callbacks during a small scroll nudge and
 * report how many took longer than 50ms. A high jank count means the page is
 * shipping a main-thread-blocking render loop, which is invisible in a
 * screenshot and obvious to a reader on a mid-range laptop.
 */
async function measureFrameStability(page) {
  return page.evaluate(
    () =>
      new Promise((resolve) => {
        const sample = 20;
        const durations = [];
        let previous = performance.now();
        let index = 0;
        let nudge = 0;

        const tick = (now) => {
          durations.push(now - previous);
          previous = now;
          index += 1;

          if (index % 6 === 0) {
            nudge = nudge === 0 ? 180 : -180;
            const root = document.documentElement;
            const previousBehavior = root.style.scrollBehavior;
            root.style.scrollBehavior = "auto";
            window.scrollBy({ top: nudge, left: 0, behavior: "instant" });
            root.style.scrollBehavior = previousBehavior;
          }

          if (index >= sample) {
            const jankFrames = durations.filter((d) => d > 50).length;
            const worst = durations.reduce((max, d) => Math.max(max, d), 0);
            const total = durations.reduce((sum, d) => sum + d, 0);
            resolve({
              frames: sample,
              jankFrames,
              worstFrameMs: Math.round(worst * 100) / 100,
              averageFrameMs: Math.round((total / sample) * 100) / 100,
            });
            return;
          }

          window.requestAnimationFrame(tick);
        };

        window.requestAnimationFrame(tick);
      })
  );
}

async function inspectViewport(browser, viewport, target, options, outDir) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
    deviceScaleFactor: viewport.deviceScaleFactor,
    isMobile: viewport.isMobile,
    hasTouch: viewport.hasTouch,
    userAgent: viewport.userAgent,
    reducedMotion: "no-preference",
  });

  const consoleErrors = [];
  const pageErrors = [];
  const failedRequests = [];

  const page = await context.newPage();
  page.on("console", (message) => {
    if (message.type() === "error") {
      consoleErrors.push({ text: message.text(), location: message.location() });
    }
  });
  page.on("pageerror", (error) => {
    pageErrors.push({ message: error.message, stack: error.stack ? error.stack.split("\n")[0] : "" });
  });
  page.on("requestfailed", (request) => {
    failedRequests.push({ url: request.url(), failure: request.failure() ? request.failure().errorText : "unknown" });
  });

  const checks = [];
  const record = (name, passed, detail) => {
    checks.push({ name, passed, detail });
    return passed;
  };

  let navigationOk = true;
  try {
    await page.goto(target.url, { waitUntil: "load", timeout: options.timeout });
    await page.waitForLoadState("networkidle", { timeout: Math.min(options.timeout, 8000) }).catch(() => {});
  } catch (error) {
    navigationOk = false;
    record("navigation", false, `failed to load ${target.url}: ${error.message}`);
  }

  if (navigationOk) {
    record("navigation", true, `loaded ${target.url}`);
  }

  const metrics = navigationOk ? await collectMetrics(page) : null;

  if (metrics) {
    record(
      "console errors",
      consoleErrors.length === 0,
      consoleErrors.length === 0
        ? "0 console.error entries"
        : `${consoleErrors.length} console.error entries`
    );
    record(
      "page errors",
      pageErrors.length === 0,
      pageErrors.length === 0
        ? "0 uncaught page errors"
        : `${pageErrors.length} uncaught page errors`
    );
    record(
      "broken images",
      metrics.brokenImages.length === 0,
      metrics.brokenImages.length === 0
        ? `all ${metrics.imageCount} image(s) decoded`
        : `${metrics.brokenImages.length} of ${metrics.imageCount} image(s) failed to decode`
    );

    const overflowed = metrics.scrollWidth > metrics.innerWidth + 1;
    record(
      "horizontal overflow",
      !overflowed,
      overflowed
        ? `scrollWidth ${metrics.scrollWidth} > innerWidth ${metrics.innerWidth}` +
            (metrics.overflowOffender
              ? ` (widest offender: <${metrics.overflowOffender.tag} id="${metrics.overflowOffender.id}" class="${metrics.overflowOffender.className}"> right=${metrics.overflowOffender.right})`
              : "")
        : `scrollWidth ${metrics.scrollWidth} <= innerWidth ${metrics.innerWidth}`
    );

    const steps = [];
    if (metrics.stepCount === 0) {
      record("scrollytelling step activation", true, "no [data-step] elements on this page");
    } else {
      for (let index = 0; index < metrics.stepCount; index += 1) {
        await scrollStepIntoBand(page, index);
        await page.waitForTimeout(options.settle);
        const state = await readStepState(page, index);
        steps.push({
          step: state ? state.id : `step-${index + 1}`,
          active: state ? state.active : false,
          activeClasses: state ? state.activeClasses : [],
          camera: state ? state.camera : null,
          layers: state ? state.layers : null,
        });
      }
      const activated = steps.filter((step) => step.active).length;
      record(
        "scrollytelling step activation",
        activated === steps.length,
        `${activated}/${steps.length} [data-step] elements reached an active state on scroll`
      );
    }

    // Axis E: the hero instrument must survive real input without throwing.
    const heroInteraction = await interactWithHero(page, consoleErrors, pageErrors);
    record(
      "interactive hero input",
      heroInteraction.passed,
      heroInteraction.detail
    );

    // Frame stability during a scroll nudge: a loop that never sleeps or a
    // shader with an unclamped DPR shows up here and nowhere else.
    const frameStability = await measureFrameStability(page);
    record(
      "frame stability",
      frameStability.jankFrames <= 2,
      `${frameStability.jankFrames}/${frameStability.frames} frame(s) over 50ms ` +
        `(worst ${frameStability.worstFrameMs}ms, average ${frameStability.averageFrameMs}ms)`
    );

    record(
      "design spells",
      metrics.spellCount >= 2 || metrics.interactiveHeroCount === 0,
      metrics.interactiveHeroCount === 0
        ? "no [data-interactive-hero] on this page, spell minimum not enforced"
        : metrics.spellCount >= 2
          ? `${metrics.spellCount} data-spell element(s): ${metrics.spellNames.join(", ")}`
          : `only ${metrics.spellCount} data-spell element(s) (${metrics.spellNames.join(", ") || "none"}); at least 2 required`
    );

    // The step loop leaves the viewport parked at the last step, which leaves
    // sticky stages stuck at the bottom of the story section. Return to the top
    // of the document so the captured frame shows the real page.
    await resetScrollToTop(page);

    const filename = `${viewport.label}-${viewport.width}x${viewport.height}.png`;
    await page.screenshot({
      path: path.join(outDir, filename),
      fullPage: options.fullPage,
    });

    await context.close();

    return {
      viewport: `${viewport.label}-${viewport.width}x${viewport.height}`,
      screenshot: filename,
      consoleErrors,
      pageErrors,
      failedRequests,
      metrics,
      steps,
      heroInteraction,
      frameStability,
      checks,
      passed: checks.every((check) => check.passed),
    };
  }

  await context.close();
  return {
    viewport: `${viewport.label}-${viewport.width}x${viewport.height}`,
    screenshot: null,
    consoleErrors,
    pageErrors,
    failedRequests,
    metrics: null,
    steps: [],
    heroInteraction: null,
    frameStability: null,
    checks,
    passed: false,
  };
}

function renderHumanSummary(results, target) {
  const lines = [];
  lines.push("playwright gauntlet summary");
  lines.push(`  target : ${target.url} (${target.kind})`);
  lines.push("");

  for (const result of results) {
    const status = result.passed ? "PASS" : "FAIL";
    lines.push(`  [${status}] ${result.viewport}`);
    if (result.screenshot) lines.push(`         screenshot: ${result.screenshot}`);
    for (const check of result.checks) {
      lines.push(`         ${check.passed ? "ok  " : "FAIL"} ${check.name}: ${check.detail}`);
    }
    for (const entry of result.consoleErrors.slice(0, 5)) {
      lines.push(`         console.error: ${entry.text}`);
    }
    for (const entry of result.pageErrors.slice(0, 5)) {
      lines.push(`         pageerror: ${entry.message}`);
    }
    for (const step of result.steps) {
      const mark = step.active ? "active" : "inactive";
      const via = step.activeClasses.length ? ` via ${step.activeClasses.join(", ")}` : "";
      lines.push(`         step ${step.step}: ${mark}${via}`);
    }
    if (result.metrics) {
      lines.push(
        `         reduced-motion media rules reachable from CSSOM: ${result.metrics.reducedMotionRules}`
      );
      lines.push(
        `         document height: ${result.metrics.pageHeight}px, title: ${result.metrics.title || "(none)"}`
      );
      lines.push(
        `         interactive hero elements: ${result.metrics.interactiveHeroCount}, ` +
          `design spells: ${result.metrics.spellCount}` +
          (result.metrics.spellNames.length
            ? ` (${result.metrics.spellNames.join(", ")})`
            : "")
      );
      if (result.frameStability) {
        lines.push(
          `         frame stability: ${result.frameStability.jankFrames}/${result.frameStability.frames} ` +
            `jank frames, worst ${result.frameStability.worstFrameMs}ms, ` +
            `average ${result.frameStability.averageFrameMs}ms`
        );
      }
      if (result.failedRequests.length) {
        lines.push(`         informational: ${result.failedRequests.length} failed request(s)`);
      }
    }
    lines.push("");
  }

  const failed = results.reduce((total, result) => total + result.checks.filter((check) => !check.passed).length, 0);
  lines.push(failed === 0 ? "  ALL CHECKS PASSED" : `  ${failed} CHECK(S) FAILED`);
  return lines.join("\n");
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const target = resolveTarget(options.url);

  const playwright = await loadPlaywright();
  if (!playwright) {
    process.stderr.write(`${INSTALL_HINT}\n`);
    process.exit(2);
  }

  const outDir = path.resolve(process.cwd(), options.out);
  await mkdir(outDir, { recursive: true });

  let browser;
  try {
    browser = await playwright.chromium.launch({ headless: !options.headed });
  } catch (error) {
    process.stderr.write(
      [
        "Chromium could not be launched: " + error.message,
        "",
        "Install the browser binary with:",
        "  npx playwright install chromium",
        "or on a headless Linux host with:",
        "  npx playwright install --with-deps chromium",
        "",
        "Stage 6 is BLOCKED until a real browser run succeeds.",
      ].join("\n") + "\n"
    );
    process.exit(2);
  }

  const results = [];
  try {
    for (const viewport of VIEWPORTS) {
      const result = await inspectViewport(browser, viewport, target, options, outDir);
      results.push(result);
    }
  } finally {
    await browser.close();
  }

  const summary = {
    tool: "playwright_gauntlet",
    target: target.url,
    targetKind: target.kind,
    outDir,
    fullPage: options.fullPage,
    viewports: results.map((result) => result.viewport),
    passed: results.every((result) => result.passed),
    results,
  };

  await writeFile(path.join(outDir, "report.json"), `${JSON.stringify(summary, null, 2)}\n`, "utf8");

  process.stdout.write(`${renderHumanSummary(results, target)}\n`);
  process.stdout.write("--- JSON ---\n");
  process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);

  process.exit(summary.passed ? 0 : 1);
}

main().catch((error) => {
  process.stderr.write(`playwright gauntlet crashed: ${error && error.stack ? error.stack : error}\n`);
  process.exit(2);
});
