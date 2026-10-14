# Spoke 06: Creative Technologist (Shaders, Physics, and Design Spells)

**Load this file only when you are running Stage 5, and only when
`DESIGN_VARIANCE >= 6` or `MOTION_INTENSITY >= 6`.**

This spoke is for the last 5 percent. Everything in spoke 04 gets a page to
"correct". This spoke gets the page an instrument. The rules:

- A hero is not a headline plus a screenshot. It is a **playable centerpiece**
  marked `data-interactive-hero`, and it must respond within 100ms of input.
- Every tactile effect is a named **Design Spell**, marked
  `data-spell="<name>"`, and at least two must be live. Unnamed delight is
  indistinguishable from noise.
- One motion source per page. A spring solver and a shader both driving layout
  will fight, and the reader will feel it as sluggishness.
- Everything below degrades. Reduced motion gets a still frame, not a broken
  one. Zero idle CPU is a requirement, not an optimization.

## 1. Blueprint 1: Zero-Dependency WebGL Stage

`<canvas data-interactive-hero data-shader-stage>` with a full-screen quad, a
domain-warped noise field, and tactile dithering. Pointer-lerped so the cursor
never snaps, which is the difference between "reacts" and "feels alive".

```html
<canvas
  id="shader-stage"
  data-interactive-hero
  data-shader-stage
  aria-label="Live field responding to pointer position"
  role="img"
></canvas>
```

```glsl
// Vertex shader: one full-screen quad, clip space, no matrices needed.
attribute vec2 a_position;
varying vec2 v_uv;

void main() {
  v_uv = a_position * 0.5 + 0.5;
  gl_Position = vec4(a_position, 0.0, 1.0);
}
```

```glsl
// Fragment shader: domain-warped fbm, pointer-warped, ordered dither.
precision highp float;

uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_pointer;
uniform float u_scroll;

varying vec2 v_uv;

vec2 hash2(vec2 p) {
  p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
  return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
}

float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(
    mix(dot(hash2(i + vec2(0.0, 0.0)), f - vec2(0.0, 0.0)),
        dot(hash2(i + vec2(1.0, 0.0)), f - vec2(1.0, 0.0)), u.x),
    mix(dot(hash2(i + vec2(0.0, 1.0)), f - vec2(0.0, 1.0)),
        dot(hash2(i + vec2(1.0, 1.0)), f - vec2(1.0, 1.0)), u.x),
    u.y
  );
}

float fbm(vec2 p) {
  float value = 0.0;
  float amplitude = 0.5;
  mat2 rotation = mat2(0.80, 0.60, -0.60, 0.80);
  for (int i = 0; i < 5; i++) {
    value += amplitude * noise(p);
    p = rotation * p * 2.02;
    amplitude *= 0.5;
  }
  return value;
}

void main() {
  vec2 uv = (v_uv * u_resolution - 0.5 * u_resolution)
            / min(u_resolution.x, u_resolution.y);

  float t = u_time * 0.06;
  vec2 pointer = u_pointer * 2.0 - 1.0;
  pointer.y = -pointer.y;

  vec2 warp = vec2(
    fbm(uv * 1.6 + vec2(0.0, t) + vec2(u_scroll * 0.25)),
    fbm(uv * 1.6 + vec2(5.2, 1.3) - t + vec2(u_scroll * 0.18))
  );

  float base = fbm(uv * 2.2 + warp * 1.8 + pointer * 0.22);
  float field = smoothstep(-0.25, 0.85, base + warp.x * 0.35);

  vec3 deep = vec3(0.04, 0.05, 0.07);
  vec3 mid = vec3(0.10, 0.28, 0.33);
  vec3 glow = vec3(0.32, 0.78, 0.85);

  vec3 color = mix(deep, mid, smoothstep(0.0, 0.6, field));
  color = mix(
    color,
    glow,
    smoothstep(0.55, 1.0, field) * (0.35 + 0.35 * length(pointer))
  );

  float dither = (fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233)))
                        * 43758.5453) - 0.5) / 255.0;
  color += dither;

  gl_FragColor = vec4(color, 1.0);
}
```

```js
// Zero-dependency WebGL stage with pointer lerp, DPR clamp, IO pause, and a
// single static frame under prefers-reduced-motion.
const canvas = document.getElementById('shader-stage');
const gl = canvas.getContext('webgl', { antialias: false, alpha: false });
if (gl) {
  const VERTEX_SRC = `
attribute vec2 a_position;
varying vec2 v_uv;
void main() {
  v_uv = a_position * 0.5 + 0.5;
  gl_Position = vec4(a_position, 0.0, 1.0);
}`;

  const FRAGMENT_SRC = `
precision highp float;
uniform vec2 u_resolution;
uniform float u_time;
uniform vec2 u_pointer;
uniform float u_scroll;
varying vec2 v_uv;
vec2 hash2(vec2 p) {
  p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
  return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
}
float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(
    mix(dot(hash2(i + vec2(0.0, 0.0)), f - vec2(0.0, 0.0)),
        dot(hash2(i + vec2(1.0, 0.0)), f - vec2(1.0, 0.0)), u.x),
    mix(dot(hash2(i + vec2(0.0, 1.0)), f - vec2(0.0, 1.0)),
        dot(hash2(i + vec2(1.0, 1.0)), f - vec2(1.0, 1.0)), u.x),
    u.y);
}
float fbm(vec2 p) {
  float value = 0.0;
  float amplitude = 0.5;
  mat2 rotation = mat2(0.80, 0.60, -0.60, 0.80);
  for (int i = 0; i < 5; i++) {
    value += amplitude * noise(p);
    p = rotation * p * 2.02;
    amplitude *= 0.5;
  }
  return value;
}
void main() {
  vec2 uv = (v_uv * u_resolution - 0.5 * u_resolution)
            / min(u_resolution.x, u_resolution.y);
  float t = u_time * 0.06;
  vec2 pointer = u_pointer * 2.0 - 1.0;
  pointer.y = -pointer.y;
  vec2 warp = vec2(
    fbm(uv * 1.6 + vec2(0.0, t) + vec2(u_scroll * 0.25)),
    fbm(uv * 1.6 + vec2(5.2, 1.3) - t + vec2(u_scroll * 0.18)));
  float base = fbm(uv * 2.2 + warp * 1.8 + pointer * 0.22);
  float field = smoothstep(-0.25, 0.85, base + warp.x * 0.35);
  vec3 deep = vec3(0.04, 0.05, 0.07);
  vec3 mid = vec3(0.10, 0.28, 0.33);
  vec3 glow = vec3(0.32, 0.78, 0.85);
  vec3 color = mix(deep, mid, smoothstep(0.0, 0.6, field));
  color = mix(color, glow,
    smoothstep(0.55, 1.0, field) * (0.35 + 0.35 * length(pointer)));
  float dither = (fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233)))
                        * 43758.5453) - 0.5) / 255.0;
  color += dither;
  gl_FragColor = vec4(color, 1.0);
}`;

  function compileShader(type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      const log = gl.getShaderInfoLog(shader);
      gl.deleteShader(shader);
      throw new Error('[shader] compile failed: ' + log);
    }
    return shader;
  }

  function buildProgram() {
    const program = gl.createProgram();
    gl.attachShader(program, compileShader(gl.VERTEX_SHADER, VERTEX_SRC));
    gl.attachShader(program, compileShader(gl.FRAGMENT_SHADER, FRAGMENT_SRC));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      throw new Error('[shader] link failed: ' + gl.getProgramInfoLog(program));
    }
    gl.useProgram(program);
    return program;
  }

  const program = buildProgram();

  const quad = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, quad);
  gl.bufferData(
    gl.ARRAY_BUFFER,
    new Float32Array([-1, -1, 3, -1, -1, 3]),
    gl.STATIC_DRAW
  );
  const positionLocation = gl.getAttribLocation(program, 'a_position');
  gl.enableVertexAttribArray(positionLocation);
  gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

  const uResolution = gl.getUniformLocation(program, 'u_resolution');
  const uTime = gl.getUniformLocation(program, 'u_time');
  const uPointer = gl.getUniformLocation(program, 'u_pointer');
  const uScroll = gl.getUniformLocation(program, 'u_scroll');

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const pointerTarget = { x: 0.5, y: 0.5 };
  const pointerCurrent = { x: 0.5, y: 0.5 };

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(1, Math.floor(canvas.clientWidth * dpr));
    const height = Math.max(1, Math.floor(canvas.clientHeight * dpr));
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
      gl.viewport(0, 0, width, height);
    }
    gl.uniform2f(uResolution, width, height);
  }

  function onPointerMove(event) {
    const rect = canvas.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return;
    pointerTarget.x = (event.clientX - rect.left) / rect.width;
    pointerTarget.y = 1 - (event.clientY - rect.top) / rect.height;
  }

  canvas.addEventListener('pointermove', onPointerMove, { passive: true });
  canvas.addEventListener('pointerleave', () => {
    pointerTarget.x = 0.5;
    pointerTarget.y = 0.5;
  }, { passive: true });

  let scrollProgress = 0;
  function onScroll() {
    const rect = canvas.getBoundingClientRect();
    const span = window.innerHeight + rect.height;
    scrollProgress = Math.min(Math.max(-rect.top / span, 0), 1);
  }
  window.addEventListener('scroll', onScroll, { passive: true });

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function draw(seconds) {
    resize();
    const settle = reducedMotion.matches ? 1 : 0.08;
    pointerCurrent.x = lerp(pointerCurrent.x, pointerTarget.x, settle);
    pointerCurrent.y = lerp(pointerCurrent.y, pointerTarget.y, settle);
    gl.uniform1f(uTime, reducedMotion.matches ? 12.5 : seconds);
    gl.uniform2f(uPointer, pointerCurrent.x, pointerCurrent.y);
    gl.uniform1f(uScroll, scrollProgress);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  let frameId = 0;
  let visible = true;
  const startedAt = performance.now();

  function loop(now) {
    draw((now - startedAt) / 1000);
    frameId = window.requestAnimationFrame(loop);
  }

  function renderStaticFrame() {
    if (frameId) {
      window.cancelAnimationFrame(frameId);
      frameId = 0;
    }
    draw(12.5);
  }

  function start() {
    if (frameId || !visible) return;
    frameId = window.requestAnimationFrame(loop);
  }

  function pause() {
    if (!frameId) return;
    window.cancelAnimationFrame(frameId);
    frameId = 0;
  }

  function syncMotionMode() {
    if (reducedMotion.matches) renderStaticFrame();
    else start();
  }

  new IntersectionObserver((entries) => {
    visible = entries[0].isIntersecting;
    if (visible) syncMotionMode();
    else pause();
  }, { threshold: 0 }).observe(canvas);

  reducedMotion.addEventListener('change', syncMotionMode);
  window.addEventListener('resize', resize, { passive: true });
  onScroll();
  syncMotionMode();
}
```

Performance guardrails, all non-negotiable:

- `Math.min(window.devicePixelRatio || 1, 2)` caps fill rate. Never use raw DPR
  on a full-screen quad; a 3x phone will melt.
- The `IntersectionObserver` pauses the `requestAnimationFrame` loop offscreen.
  A shader that burns battery behind a fold is a bug, not a feature.
- Under `prefers-reduced-motion: reduce`, render exactly one static frame at a
  fixed `u_time`. Never `u_time: 0`, which lands on the flat part of the field.
- Lerp the pointer. A cursor that snaps on a shader looks like a bug; one that
  eases reads as mass.

## 2. Blueprint 2: React Three Fiber Custom Shader Stage

For React and Next.js projects. `dpr={[1, 1.5]}`, pointer-lerped uniforms in
`useFrame`, and a reduced-motion fallback that renders a still frame.

```tsx
"use client";

import { useMemo, useRef } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";

const vertexShader = /* glsl */ `
  varying vec2 v_uv;
  void main() {
    v_uv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const fragmentShader = /* glsl */ `
  precision highp float;
  uniform float u_time;
  uniform vec2 u_pointer;
  uniform vec3 u_deep;
  uniform vec3 u_glow;
  varying vec2 v_uv;

  vec2 hash2(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
  }

  float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(
      mix(dot(hash2(i), f), dot(hash2(i + vec2(1.0, 0.0)), f - vec2(1.0, 0.0)), u.x),
      mix(dot(hash2(i + vec2(0.0, 1.0)), f - vec2(0.0, 1.0)),
          dot(hash2(i + vec2(1.0, 1.0)), f - vec2(1.0, 1.0)), u.x),
      u.y);
  }

  float fbm(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;
    for (int i = 0; i < 4; i++) {
      value += amplitude * noise(p);
      p = mat2(0.80, 0.60, -0.60, 0.80) * p * 2.02;
      amplitude *= 0.5;
    }
    return value;
  }

  void main() {
    vec2 uv = v_uv - 0.5;
    vec2 pointer = u_pointer - 0.5;
    vec2 warp = vec2(fbm(uv * 3.0 + u_time * 0.1),
                     fbm(uv * 3.0 + vec2(4.7, 2.1) - u_time * 0.08));
    float field = smoothstep(-0.2, 0.9, fbm(uv * 4.5 + warp * 2.0 + pointer));
    vec3 color = mix(u_deep, u_glow, field);
    gl_FragColor = vec4(color, 1.0);
  }
`;

function FieldPlane({ reducedMotion }: { reducedMotion: boolean }) {
  const materialRef = useRef<THREE.ShaderMaterial | null>(null);
  const { viewport } = useThree();

  const uniforms = useMemo(
    () => ({
      u_time: { value: reducedMotion ? 12.5 : 0 },
      u_pointer: { value: new THREE.Vector2(0.5, 0.5) },
      u_deep: { value: new THREE.Color("#0a0f12") },
      u_glow: { value: new THREE.Color("#37b7c4") },
    }),
    [reducedMotion]
  );

  useFrame((state, delta) => {
    const material = materialRef.current;
    if (!material) return;

    if (reducedMotion) {
      material.uniforms.u_time.value = 12.5;
      material.uniforms.u_pointer.value.set(0.5, 0.5);
      return;
    }

    material.uniforms.u_time.value += delta;
    const targetX = state.pointer.x * 0.5 + 0.5;
    const targetY = state.pointer.y * 0.5 + 0.5;
    const uniformsNow = material.uniforms.u_pointer.value as THREE.Vector2;
    uniformsNow.x += (targetX - uniformsNow.x) * 0.08;
    uniformsNow.y += (targetY - uniformsNow.y) * 0.08;
  });

  return (
    <mesh scale={[viewport.width * 0.6, viewport.height * 0.6, 1]}>
      <planeGeometry args={[2, 2, 1, 1]} />
      <shaderMaterial
        ref={materialRef}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        depthWrite={false}
        depthTest={false}
      />
    </mesh>
  );
}

export function ShaderHero() {
  const reducedMotion =
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  return (
    <figure
      data-interactive-hero
      className="shader-hero"
      aria-label="Live field responding to pointer position"
      role="img"
    >
      <Canvas
        dpr={[1, 1.5]}
        frameloop={reducedMotion ? "demand" : "always"}
        gl={{ antialias: false, alpha: false, powerPreference: "high-performance" }}
        camera={{ position: [0, 0, 1] }}
      >
        <FieldPlane reducedMotion={reducedMotion} />
      </Canvas>
    </figure>
  );
}

export default ShaderHero;
```

R3F rules:

- `dpr={[1, 1.5]}` caps fill rate. An uncapped `<Canvas>` is the single most
  common cause of a janky hero on mobile.
- `frameloop="demand"` under reduced motion, plus a fixed `u_time`, gives a
  still frame that still looks composed.
- Lerp `state.pointer` in `useFrame`. Never bind it straight to the uniform.
- `powerPreference: "high-performance"` keeps the page on the discrete GPU
  where one exists.

## 3. Blueprint 3: Critically Damped Spring Engine

Hooke's law, `F = -k * x - c * v`, integrated per frame and **auto-sleeping**
when displacement and velocity both settle below `0.001`. A spring loop that
never stops is a battery bug, so the rest condition is mandatory.

```js
// Critically damped spring solver with a rest threshold and auto-sleep.
class Spring {
  constructor({ stiffness = 180, damping = 22, mass = 1, restDisplacement = 0.001, restVelocity = 0.001 } = {}) {
    this.stiffness = stiffness;
    this.damping = damping;
    this.mass = mass;
    this.restDisplacement = restDisplacement;
    this.restVelocity = restVelocity;
    this.value = 0;
    this.target = 0;
    this.velocity = 0;
    this.asleep = true;
  }

  setTarget(next) {
    if (next !== this.target) {
      this.target = next;
      this.asleep = false;
    }
  }

  nudge(amount) {
    this.velocity += amount;
    this.asleep = false;
  }

  step(dt) {
    if (this.asleep) return this.value;
    const clamped = Math.min(dt, 1 / 30);
    const force = -this.stiffness * (this.value - this.target);
    const drag = -this.damping * this.velocity;
    const acceleration = (force + drag) / this.mass;
    this.velocity += acceleration * clamped;
    this.value += this.velocity * clamped;
    if (
      Math.abs(this.value - this.target) < this.restDisplacement &&
      Math.abs(this.velocity) < this.restVelocity
    ) {
      this.value = this.target;
      this.velocity = 0;
      this.asleep = true;
    }
    return this.value;
  }
}

// Magnetic targets: pull toward the pointer inside a radius, overshoot back.
class MagneticField {
  constructor(items, { radius = 140, strength = 0.32 } = {}) {
    this.radius = radius;
    this.strength = strength;
    this.entries = items.map((element) => ({
      element,
      x: new Spring({ stiffness: 210, damping: 17 }),
      y: new Spring({ stiffness: 210, damping: 17 }),
    }));
    this.pointer = { x: 0, y: 0, active: false };
    this.frameId = 0;
    this.last = 0;
    this.reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  }

  attach() {
    for (const entry of this.entries) {
      const node = entry.element;
      node.addEventListener('pointerenter', (event) => {
        this.pointer.x = event.clientX;
        this.pointer.y = event.clientY;
        this.pointer.active = true;
        this.wake();
      });
      node.addEventListener('pointermove', (event) => {
        this.pointer.x = event.clientX;
        this.pointer.y = event.clientY;
        this.wake();
      });
      node.addEventListener('pointerleave', () => {
        this.pointer.active = false;
        this.wake();
      });
    }
    window.addEventListener('pointermove', (event) => {
      this.pointer.x = event.clientX;
      this.pointer.y = event.clientY;
    }, { passive: true });
  }

  wake() {
    if (this.reduced.matches || this.frameId) return;
    this.last = performance.now();
    this.frameId = window.requestAnimationFrame((now) => this.tick(now));
  }

  tick(now) {
    const dt = (now - this.last) / 1000;
    this.last = now;
    let moving = false;

    for (const entry of this.entries) {
      const rect = entry.element.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      if (this.pointer.active && !this.reduced.matches) {
        const dx = this.pointer.x - centerX;
        const dy = this.pointer.y - centerY;
        const distance = Math.hypot(dx, dy);
        if (distance < this.radius && distance > 0.001) {
          const falloff = 1 - distance / this.radius;
          entry.x.setTarget(dx * this.strength * falloff);
          entry.y.setTarget(dy * this.strength * falloff);
        } else {
          entry.x.setTarget(0);
          entry.y.setTarget(0);
        }
      } else {
        entry.x.setTarget(0);
        entry.y.setTarget(0);
      }

      const x = entry.x.step(dt);
      const y = entry.y.step(dt);
      if (!entry.x.asleep || !entry.y.asleep) moving = true;
      entry.element.style.transform = `translate3d(${x.toFixed(2)}px, ${y.toFixed(2)}px, 0)`;
    }

    this.frameId = moving ? window.requestAnimationFrame((next) => this.tick(next)) : 0;
  }
}

const magnetic = new MagneticField(
  Array.from(document.querySelectorAll('[data-spell="magnetic-spring"]'))
);
magnetic.attach();
```

Physics notes:

- `damping` near `2 * sqrt(stiffness * mass)` is critically damped: fast
  approach, no ringing. Drop below it and the element oscillates, which reads
  as cheap.
- The auto-sleep threshold is what makes this acceptable. When
  `|value - target| < 0.001` and `|velocity| < 0.001`, zero the spring and stop
  scheduling frames. Idle CPU returns to exactly zero.
- Under `prefers-reduced-motion: reduce`, `wake()` never starts the loop and
  every transform stays at the identity.
- Animate `transform` only. Never `top` or `left`.

## 4. Blueprint 4: Procedural SVG Filter Arsenal

Zero asset bytes, GPU-composited, and they work on `<img>` content you did not
draw. Park the definitions once, reference them by `filter: url(#id)`.

```html
<svg aria-hidden="true" width="0" height="0" focusable="false" class="filter-defs">
  <defs>
    <filter id="analog-grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence
        type="fractalNoise"
        baseFrequency="0.8"
        numOctaves="3"
        stitchTiles="stitch"
        result="noise"
      />
      <feColorMatrix
        in="noise"
        type="matrix"
        values="
          0 0 0 0 0.5
          0 0 0 0 0.5
          0 0 0 0 0.5
          0 0 0 0.35 0"
        result="grain"
      />
      <feBlend in="SourceGraphic" in2="grain" mode="overlay" />
    </filter>

    <filter id="liquid-refraction" x="-20%" y="-20%" width="140%" height="140%">
      <feTurbulence
        type="fractalNoise"
        baseFrequency="0.012 0.028"
        numOctaves="2"
        seed="7"
        result="ripple"
      />
      <feDisplacementMap
        in="SourceGraphic"
        in2="ripple"
        scale="18"
        xChannelSelector="R"
        yChannelSelector="G"
      />
    </filter>

    <filter id="gooey-metaball" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
      <feColorMatrix
        in="blur"
        type="matrix"
        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 22 -9"
        result="goo"
      />
      <feBlend in="SourceGraphic" in2="goo" />
    </filter>
  </defs>
</svg>
```

```css
.grain-surface {
  filter: url(#analog-grain);
}

/* Liquid refraction, driven by hover and scroll without touching the filter
   definition itself. */
.refract {
  filter: url(#liquid-refraction);
  transition: filter 240ms var(--ease-out), transform 240ms var(--ease-out);
}
.refract:hover {
  transform: scale(1.03);
}
@media (prefers-reduced-motion: reduce) {
  .grain-surface { filter: none; }
  .refract { filter: none; }
  .refract:hover { transform: none; }
}
```

Filter rules:

- The `<defs>` svg must be `aria-hidden="true"` with `width="0" height="0"`, or
  screen readers announce an empty graphic.
- `#analog-grain` at `numOctaves="3"` is roughly 4ms on a modern GPU and zero
  on layout. `numOctaves` above 4 is wasted.
- `#gooey-metaball` depends on the `22 -9` alpha threshold in the
  `feColorMatrix`. Lower the `22` and the blobs separate; raise it and they
  vanish.
- Any of these must be dropped to `filter: none` under reduced motion. A
  full-screen animated turbulence is a genuine accessibility failure, and
  triggers nausea for some readers.

## 5. Blueprint 5: Design Spells

### 5.1 Web Audio Micro-Synth (opt-in only)

A 12ms filtered mechanical click, generated with zero audio assets. **Never**
autoplay. The control defaults to muted and the context is only created after
an explicit user gesture.

```html
<button
  type="button"
  class="sound-toggle"
  data-spell="sound-toggle"
  aria-pressed="false"
  aria-label="Enable interface click sounds"
>
  <span class="sound-toggle__icon" aria-hidden="true"></span>
  <span class="sound-toggle__label">Sounds off</span>
</button>
```

```js
class TactileSynth {
  constructor() {
    this.enabled = false;
    this.context = null;
  }

  ensureContext() {
    if (!this.context) {
      const Constructor = window.AudioContext || window.webkitAudioContext;
      if (!Constructor) return null;
      this.context = new Constructor();
    }
    if (this.context.state === 'suspended') this.context.resume();
    return this.context;
  }

  click() {
    if (!this.enabled) return;
    const context = this.ensureContext();
    if (!context) return;

    const now = context.currentTime;
    const duration = 0.012;

    const oscillator = context.createOscillator();
    oscillator.type = 'triangle';
    oscillator.frequency.setValueAtTime(1180, now);
    oscillator.frequency.exponentialRampToValueAtTime(420, now + duration);

    const bufferLength = Math.floor(context.sampleRate * duration);
    const noiseBuffer = context.createBuffer(1, bufferLength, context.sampleRate);
    const channel = noiseBuffer.getChannelData(0);
    for (let i = 0; i < bufferLength; i += 1) {
      channel[i] = (Math.random() * 2 - 1) * (1 - i / bufferLength);
    }

    const noise = context.createBufferSource();
    noise.buffer = noiseBuffer;

    const filter = context.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(2400, now);
    filter.Q.setValueAtTime(1.2, now);

    const gain = context.createGain();
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(0.18, now + 0.002);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

    oscillator.connect(filter);
    noise.connect(filter);
    filter.connect(gain);
    gain.connect(context.destination);

    oscillator.start(now);
    noise.start(now);
    oscillator.stop(now + duration);
    noise.stop(now + duration);
  }
}

const synth = new TactileSynth();
const soundToggle = document.querySelector('[data-spell="sound-toggle"]');

if (soundToggle) {
  soundToggle.addEventListener('click', () => {
    synth.enabled = !synth.enabled;
    soundToggle.setAttribute('aria-pressed', String(synth.enabled));
    const label = soundToggle.querySelector('.sound-toggle__label');
    if (label) label.textContent = synth.enabled ? 'Sounds on' : 'Sounds off';
    if (synth.enabled) synth.click();
  });
}

for (const target of document.querySelectorAll('[data-spell="magnetic-spring"]')) {
  target.addEventListener('pointerdown', () => synth.click());
}
```

Audio rules, non-negotiable:

- Default **muted**. The `AudioContext` is constructed only after a real user
  gesture, so autoplay policy is never violated.
- `[data-spell="sound-toggle"]` must expose `aria-pressed` so the state is
  announced, not just drawn.
- Keep clicks under 20ms. Anything longer becomes a "beep" and reads as an
  error tone.

### 5.2 Keyboard Hotkey HUD

`1`-`5` jump to major sections and flash the matching keycap. `?` or `Cmd+K`
opens an index overlay, morphing through the View Transitions API when the
browser supports it.

```html
<nav class="keycaps" data-spell="hotkey-hud" aria-label="Section shortcuts">
  <button type="button" class="keycap" data-jump="hero" data-key="1"><kbd>1</kbd> Overview</button>
  <button type="button" class="keycap" data-jump="story" data-key="2"><kbd>2</kbd> Path</button>
  <button type="button" class="keycap" data-jump="regions" data-key="3"><kbd>3</kbd> Regions</button>
  <button type="button" class="keycap" data-jump="budget" data-key="4"><kbd>4</kbd> Budget</button>
  <button type="button" class="keycap" data-jump="start" data-key="5"><kbd>5</kbd> Start</button>
</nav>

<dialog id="index-overlay" class="index-overlay" aria-label="Section index">
  <form method="dialog">
    <button type="submit" class="index-overlay__close" aria-label="Close index">Close</button>
  </form>
  <ul>
    <li><button type="button" data-jump="hero">Overview</button></li>
    <li><button type="button" data-jump="story">Path</button></li>
    <li><button type="button" data-jump="regions">Regions</button></li>
    <li><button type="button" data-jump="budget">Budget</button></li>
    <li><button type="button" data-jump="start">Start</button></li>
  </ul>
</dialog>
```

```js
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const overlay = document.getElementById('index-overlay');

function scrollToSection(id) {
  const target = document.getElementById(id);
  if (!target) return;
  target.scrollIntoView({
    behavior: reducedMotion.matches ? 'auto' : 'smooth',
    block: 'start',
  });
  const keycap = document.querySelector(`.keycap[data-key][data-jump="${id}"]`);
  if (keycap) {
    keycap.classList.remove('is-flashing');
    window.requestAnimationFrame(() => keycap.classList.add('is-flashing'));
  }
}

function morph(update) {
  if (typeof document.startViewTransition === 'function' && !reducedMotion.matches) {
    document.startViewTransition(update);
  } else {
    update();
  }
}

function openOverlay() {
  morph(() => {
    if (typeof overlay.showModal === 'function') overlay.showModal();
    else overlay.setAttribute('open', '');
  });
}

function closeOverlay() {
  morph(() => {
    if (typeof overlay.close === 'function' && overlay.open) overlay.close();
    else overlay.removeAttribute('open');
  });
}

document.addEventListener('click', (event) => {
  const jump = event.target.closest('[data-jump]');
  if (jump) {
    event.preventDefault();
    scrollToSection(jump.dataset.jump);
  }
});

document.addEventListener('keydown', (event) => {
  if (event.metaKey || event.ctrlKey || event.altKey) return;
  const target = event.target;
  if (target instanceof HTMLElement) {
    const tag = target.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || target.isContentEditable) return;
  }

  if (event.key >= '1' && event.key <= '5') {
    const keycap = document.querySelector(`.keycap[data-key="${event.key}"]`);
    if (keycap) {
      event.preventDefault();
      scrollToSection(keycap.dataset.jump);
    }
    return;
  }

  if (event.key === '?' || ((event.metaKey || event.ctrlKey) && event.key === 'k')) {
    event.preventDefault();
    if (overlay.open) closeOverlay();
    else openOverlay();
  }

  if (event.key === 'Escape' && overlay.open) closeOverlay();
});
```

```css
.keycap {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-height: 44px;
  padding-inline: 0.75rem;
  border: 1px solid var(--surface-border);
  border-radius: var(--radius-pill);
  background: var(--surface-elevated);
  color: var(--ink-secondary);
  font: inherit;
  cursor: pointer;
  transition: background var(--dur-control) var(--ease-out),
              color var(--dur-control) var(--ease-out);
}
.keycap kbd {
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  padding: 0.1rem 0.4rem;
  border-radius: var(--radius-sm);
  background: var(--surface-sunken);
}
.keycap:hover { background: var(--accent-wash); color: var(--ink-primary); }
.keycap:focus-visible {
  outline: 2px solid var(--ink-accent);
  outline-offset: 2px;
}
.keycap.is-flashing {
  background: var(--ink-accent);
  color: var(--ink-inverse);
  transition: none;
}

::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 260ms;
  animation-timing-function: cubic-bezier(0.22, 1, 0.36, 1);
}

@media (prefers-reduced-motion: reduce) {
  .keycap.is-flashing { transition: none; }
  ::view-transition-old(root),
  ::view-transition-new(root) { animation: none; }
}
```

Hotkey rules:

- Never hijack digits while a text field has focus. The `INPUT` /
  `TEXTAREA` / `isContentEditable` guard is not optional.
- `document.startViewTransition` is feature-detected. Older browsers get the
  direct update, which is correct behavior, not a degraded one.
- `?` opens the index and `Escape` closes it. Both must work with the keyboard
  alone.
- Keycaps need `min-height: 44px` to clear the touch target floor even though
  they are primarily a keyboard affordance.

## 6. Wiring the Hero Together

The minimum shippable set for `DESIGN_VARIANCE >= 6`:

```html
<header class="hero" data-interactive-hero data-shader-stage>
  <canvas class="hero__canvas" aria-label="Live edge field" role="img"></canvas>
  <div class="hero__copy">
    <h1 class="hero__title">A request leaves the edge in 4 ms</h1>
    <p class="hero__lede">Four boundaries, one stalled hop, zero dashboards.</p>
    <div class="hero__actions">
      <a class="btn" href="#story" data-spell="magnetic-spring">Trace a request</a>
      <a class="btn btn--ghost" href="#start" data-spell="magnetic-spring">Read the budget</a>
    </div>
  </div>
  <nav class="keycaps" data-spell="hotkey-hud" aria-label="Section shortcuts">
    <button type="button" class="keycap" data-jump="story" data-key="1"><kbd>1</kbd> Path</button>
    <button type="button" class="keycap" data-jump="regions" data-key="2"><kbd>2</kbd> Regions</button>
    <button type="button" class="keycap" data-jump="budget" data-key="3"><kbd>4</kbd> Budget</button>
    <button type="button" class="keycap" data-jump="start" data-key="5"><kbd>5</kbd> Start</button>
  </nav>
</header>
```

## 7. Pre-Flight Self Audit

- `data-interactive-hero` is present and responds to pointer input.
- At least 2 distinct `data-spell="..."` values exist and are wired, not just
  declared.
- `devicePixelRatio` is clamped to 2 (vanilla) or `1.5` (R3F).
- An `IntersectionObserver` pauses the render loop when the stage is offscreen.
- `prefers-reduced-motion: reduce` yields a still frame and zero loop.
- The spring engine auto-sleeps below `0.001`, so idle CPU is zero.
- Web Audio defaults to muted and only starts after a user gesture.
- Keyboard digits are not hijacked while a text field is focused.
- Every interactive element clears `min-height: 44px` and `:focus-visible`.
- `view-transition-name` collisions are avoided; morphs are feature-detected.

Then run:

```bash
python3 <skill-dir>/scripts/verify_gate.py --phase 5 --dir .studio --target <entry-file-or-src-dir>
python3 <skill-dir>/scripts/verify_gate.py --phase 6 --dir .studio --target <entry-file-or-src-dir>
```

Quote both printed gate lines verbatim.
