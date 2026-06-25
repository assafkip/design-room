# Build Palette — vetted repo menu for design-room

Last refreshed: 2026-06-25

This palette is maintained by the **weekly modernity pulse**
(`scripts/design_room_pulse.py`): a scheduled job evaluates new repos/trends
and promotes/rejects them here, stamping the date above. The per-run design flow
does ZERO web research — it reads this palette and the attention canon, nothing
live. Pick by what the spec needs; do not pull everything. License is a non-issue
here (personal site) — "no license" repos are fine to use, just noted.

Install commands assume a Vite/Next + Tailwind project unless stated.

---

## Signature motion (pick ONE hero moment, not five)

| Repo | Install | Unlocks | License |
|---|---|---|---|
| [rdev/liquid-glass-react](https://github.com/rdev/liquid-glass-react) | `npm i liquid-glass-react` | React Liquid Glass nav/cards/modals | MIT |
| [AndrewPrifer/liquid-dom](https://github.com/AndrewPrifer/liquid-dom) | clone / copy | Glass that refracts the LIVE DOM behind it (most realistic) | none |
| [shuding/liquid-glass](https://github.com/shuding/liquid-glass) | copy single file | SVG-displacement glass, drop anywhere | MIT |
| [naughtyduk/liquidGL](https://github.com/naughtyduk/liquidGL) | copy | Vanilla-JS glass for non-React | none |
| [collidingScopes/liquid-logo](https://github.com/collidingScopes/liquid-logo) | clone | Animated metallic/liquid logo treatment | MIT |

## Backgrounds & shaders (hero canvas, section dividers)

| Repo | Install | Unlocks | License |
|---|---|---|---|
| [paper-design/shaders](https://github.com/paper-design/shaders) | `npm i @paper-design/shaders-react` | Mesh/grain gradient, liquid metal, fluted glass, warp — no GLSL by hand | custom |
| [ruucm/shadergradient](https://github.com/ruucm/shadergradient) | `npm i @shadergradient/react` | Configurable animated 3D gradient backgrounds | none |
| [collidingScopes/liquid-shape-distortions](https://github.com/collidingScopes/liquid-shape-distortions) | clone | Psychedelic real-time distortion bg | MIT |
| [Motion-Core/motion-gpu](https://github.com/Motion-Core/motion-gpu) | see repo | Next-gen WebGPU visuals (forward-looking) | MIT |

## Component grab-bags (paste-ready animated UI)

| Repo | Install | Unlocks | License |
|---|---|---|---|
| [DavidHDev/react-bits](https://github.com/DavidHDev/react-bits) | `npx jsrepo add` (per component) | 130+ components: Aurora, Beams, Particles, BlobCursor, SplashCursor, PixelTrail | custom |
| [magicuidesign/magicui](https://github.com/magicuidesign/magicui) | `npx shadcn add "https://magicui.design/r/..."` | 150+ animated React/Tailwind/Motion components | MIT |
| [haydenbleasel/kibo](https://github.com/haydenbleasel/kibo) | shadcn registry | Composable production components | MIT |
| [launch-ui/launch-ui](https://github.com/launch-ui/launch-ui) | clone / copy blocks | Full landing-page kit: nav, hero, features, pricing, footer | MIT |

## Foundations (escape template sameness)

| Repo | Install | Unlocks | License |
|---|---|---|---|
| [mui/base-ui](https://github.com/mui/base-ui) | `npm i @base-ui-components/react` | Headless, accessible, fully-custom-styled primitives (Radix successor) | MIT |
| [jnsahaj/tweakcn](https://github.com/jnsahaj/tweakcn) | web tool -> export theme string | Visual shadcn/Tailwind-v4 theme editor; kills the default-shadcn look | Apache-2.0 |
| [darkroomengineering/lenis](https://github.com/darkroomengineering/lenis) | `npm i lenis` | Smooth momentum scroll; pair with GSAP ScrollTrigger | MIT |

## Spec & system (the output format)

| Repo | Install | Unlocks | License |
|---|---|---|---|
| [google-labs-code/design.md](https://github.com/google-labs-code/design.md) | `npx design-md` (CLI) | Lints the spec, exports tokens to Tailwind/CSS/W3C | Apache-2.0 |
| [voltagent/awesome-design-md](https://github.com/voltagent/awesome-design-md) | reference | 73+ brand DESIGN.md files (Stripe, Apple, Claude) to steal structure from | MIT |

## Reference galleries (steal the technique, not the pixels)

- [pulkitxm/claude-directory](https://github.com/pulkitxm/claude-directory) — AI-generated UI experiments (GLSL heroes, 3D)
- [superdesigndev/superdesign](https://github.com/superdesigndev/superdesign) — renders competing HTML drafts on an infinite canvas

---

## Selection rule
- Spec calls for "glass" -> one of the liquid-glass repos, ONE place on the page.
- Spec calls for "alive background" -> paper-design/shaders or shadergradient.
- Spec calls for "motion-heavy scroll" -> lenis + GSAP.
- Need to stand up sections fast -> launch-ui / magicui blocks, then re-skin with tweakcn so it isn't templated.
- Always: foundation on base-ui, theme via tweakcn export, spec in design.md format.
