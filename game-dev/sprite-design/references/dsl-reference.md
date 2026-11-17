# `.sprite` Container and Procedural DSL Reference

A `.sprite` file is a plain-text definition that supports two modes:

1. **Sheet-Backed Container Mode (`sheet "..."`)**: Wraps a normalized `.png` sprite sheet (such as `hero_cat.png`) with frame size, grid dimensions, and named animation tag ranges. Created automatically by `go run ./scripts normalize`.
2. **Procedural SDF and Pixel-Art Mode (`part ...`)**: Generates multi-part 2D sprites and seamless tilesets from Signed Distance Field (SDF) shapes, 4-step material ramps, and keyframed `pose` transforms without external image files.

Comments start with `//` or `#` (when not part of a `#RRGGBB` color code).

---

## 1. Sheet-Backed Container Mode (`sheet "..."`)

When `normalize` processes one or more AI sprite grids, it writes a clean `.png` sheet alongside a `.sprite` container file. You can also author or edit this `.sprite` file directly by hand.

### 1.1 Example: `hero_cat.sprite`

```text
title "hero_cat"
type sprite
sheet "hero_cat.png"
size 256x256
grid 4x8
fps 10

tag idle       0..3 pingpong
tag walk       4..7 loop
tag run        8 once, 9..11 loop
tag jump       12..15 once
tag fall       16..19 loop
tag crouch     20..23 once
tag sleep      24..27 pingpong
tag attack     28..31 once
```

### 1.2 Container Directives

| Directive | Syntax | Description |
| :--- | :--- | :--- |
| `title` | `title "<name>"` | Human-readable asset title saved in JSON manifests and QA reports. |
| `type` | `type <sprite\|tileset>` | Sets QA validation bounds (`sprite` checks `8%..92%` fill ratio and pivot stability; `tileset` checks `50%..100%` fill ratio). |
| `sheet` | `sheet "<filename.png\|filename.aseprite>"` | Relative or absolute path to the packed RGBA `.png` sprite sheet or binary `.aseprite` file. Relative paths resolve from the directory containing the `.sprite` file. |
| `size` | `size <W>x<H>` | Width and height of a single frame in pixels (`8x8` up to `1024x1024`, such as `256x256` for 2D HD or `64x64` for pixel art). |
| `grid` | `grid <Cols>x<Rows>` | Number of columns and rows in the backing `.png` sheet (`1..128`, such as `grid 4x8` for 32 frames). |
| `fps` | `fps <1..120>` | Sprite-wide frame rate in frames per second (default `10`, equivalent to `100ms` per frame). Standardizes frame duration across all tags. |
| `duration` | `duration <5..10000>ms` | Sprite-wide frame duration in milliseconds (default `100ms`). Alternative to `fps`. |
| `tag` | `tag <name> [<intro> once,] <from>..<to> <loop>` | Shorthand animation tag mapping 0-based inclusive frame indices, optional lead-in `once` frames (`tag run 8 once, 9..11 loop` or `tag run 8..9 once, 10..13 loop`), and loop mode (`loop`, `once`, `pingpong`, or `reverse`; `forward` is accepted as an alias for `loop`). |

Key-value tag attributes (`frames=0..3 loop=pingpong`) and legacy per-tag durations (`0..3 100ms pingpong`) are also accepted for backward compatibility.

---

## 2. Procedural SDF and Pixel-Art Mode (`part ...`)

When a `.sprite` file defines `part` blocks instead of `sheet "..."`, the compiler rasterizes every frame in memory from 2D Signed Distance Field (SDF) primitives and pixel stamps.

### 2.1 Top-Level Headers

```text
title "ember_slime"
type sprite
size 32x32
fps 10
palette ember
outline #1A0B0E
light -0.5,-0.7
```

- `title "<name>"`: Asset name stored in exported JSON and QA reports.
- `type <sprite|tileset>`: `sprite` enables a 1-pixel outer silhouette outline by default; `tileset` defaults to `outline none` so adjacent tiles connect without seams.
- `size <W>x<H>`: Single frame dimensions in pixels (`8x8` to `1024x1024`, default `32x32`).
- `fps <1..120>` / `duration <ms>`: Standardized sprite-wide frame rate or frame duration (default `10` FPS / `100ms`).
- `palette <name>`: Selects one of the 12 built-in Retro-HD palettes (default `genesis`).
- `outline <#RRGGBB|none>`: Overrides the palette's 1-pixel outer outline color, or disables outlining with `none`.
- `light <dx>,<dy>`: Sets the 2D directional light vector used to shade SDF surface normals across each 4-step material ramp (automatically normalized; default `-0.5,-0.7` top-left light).

---

## 3. Built-in 12 Retro-HD Palettes and 12 Material Ramps

### 3.1 Built-in Palettes (`palette <name>`)

| Palette Name | Default Outline | Visual Character and Genre Fit |
| :--- | :--- | :--- |
| `genesis` | `#0F0C1C` | SEGA Mega Drive high-contrast 9-bit punchy arcade colors |
| `snes` | `#141020` | 16-bit JRPG rich warm fantasy colors with hue-shifted shadows |
| `neogeo` | `#0A0A14` | SNK arcade cabinet heavy metallic contrast with bright speculars |
| `cyber` | `#090619` | Neon synthwave cyberpunk with deep indigo shadows |
| `noir` | `#08080C` | High-contrast gothic ink and cold moonlight |
| `forest` | `#0D1712` | Woodland moss, bark, and sun-dappled canopy tones |
| `ember` | `#1A0B0E` | Volcanic magma, charred obsidian, and forge gold |
| `ocean` | `#07131E` | Abyssal trench teal, bioluminescent cyan, and seafoam |
| `pastel` | `#23192D` | Cozy storybook soft highlights with plum outlines |
| `bloodmoon` | `#16070F` | Dark fantasy crimson eclipse, bone, and cursed steel |
| `arcane` | `#120924` | Astral violet, mystic rune gold, and mana crystal |
| `desert` | `#1C120C` | Sun-bleached sandstone, bronze, and lapis lazuli oasis |

### 3.2 Built-in 4-Step Material Ramps (`ramp=<name>`)

Every material ramp has 4 premultiplied steps (`Step 0: Deep Shadow`, `Step 1: Base Midtone`, `Step 2: Lit Surface`, `Step 3: Specular Highlight`) that tint automatically to match the active `palette`:

| Ramp Name | Step 0 (Shadow) | Step 1 (Base) | Step 2 (Light) | Step 3 (Specular) | Typical Parts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `steel` | `#2A2E45` | `#546382` | `#8FA3C7` | `#DCE8FC` | Armor plates, helmets, blades, hulls |
| `crimson` | `#4A1228` | `#8F1E38` | `#D9384A` | `#FF8A73` | Capes, plumes, hearts, ruby cores |
| `gold` | `#5C3409` | `#A86614` | `#E8AD28` | `#FFF294` | Bells, crowns, coins, hilts, trim |
| `flesh` | `#5E2C28` | `#A35743` | `#E08B6B` | `#FFD1B3` | Faces, hands, organic creatures |
| `emerald` | `#133E2B` | `#227544` | `#44B861` | `#9BF09E` | Tunics, foliage, gems, acid |
| `plasma` | `#1D1B5E` | `#2C5CC9` | `#42B6F5` | `#C7F9FF` | Energy shields, thrusters, visors |
| `obsidian` | `#14111F` | `#28243D` | `#474166` | `#78719E` | Dark fur, boots, dungeon stone |
| `bone` | `#4A3E42` | `#877875` | `#C7B8AC` | `#F7F0E4` | Skulls, claws, horns, teeth, parchment |
| `slime` | `#194538` | `#2B8A56` | `#6CD968` | `#D7FF94` | Translucent ooze, bio-gel |
| `leather` | `#361B17` | `#663626` | `#9E5B3B` | `#CFA37E` | Belts, boots, gauntlets, satchels |
| `wood` | `#2B1612` | `#522C1E` | `#824A2E` | `#B57950` | Chests, shields, staffs, crates |
| `water` | `#10264A` | `#1D4E89` | `#348AC7` | `#8CE2FF` | Ice, potions, crystals, deep water |

### 3.3 Custom Material Ramps (`ramp <name> #shadow #base #light #spec`)

Define custom 4-step ramps at the top level of a `.sprite` file, or extract them from a reference image with `go run . extract-palette character_sheet.png`:

```text
ramp cat_fur   #100E18 #1C192A #2E2942 #4A4366
ramp amber_eye #7A3E08 #C87810 #F5B818 #FFE860
```

> [!TIP]
> **Surface Ramps vs. Specular Catchlights**:
> The 2D SDF shader maps surface normals toward the `light` vector across all 4 ramp steps (`0..3`). Keep all 4 steps of surface and eye ramps within their hue family, and stamp pure-white specular glints using `pixel <x>,<y> step=3` with a bright highlight ramp.

---

## 4. Body and Prop Parts (`part`) and Primitives

A `part` groups SDF or pixel primitives into a named, Z-ordered element that can be animated independently inside `tag` blocks:

```text
part <name> [ramp=<ramp_name>] [z=<int>] [mirror_x=<true|false>] [hidden=<true|false>] [pivot=<px>,<py>] [dither=<none|bayer2|bayer4>]
```

- `ramp=<name>`: Default material ramp for primitives in this part (default `steel`).
- `z=<int>`: Painter's algorithm depth order. Lower `z` renders behind higher `z` (`z=-5` back limbs behind `z=0` torso, `z=5` front limbs in front).
- `mirror_x=true`: Mirrors the part horizontally across the frame centerline (`width / 2`).
- `hidden=true`: Hides the part by default until enabled on specific frames via `pose <part> visible=true` (useful for blinking eyelids or slash arcs).
- `pivot=<px>,<py>`: Explicit rotation and scaling pivot in frame pixel coordinates (defaults to the centroid of the part's primitives). Share the same pivot across attached parts (such as head, ears, and eyes) so they rotate together without detaching.
- `dither=<none|bayer2|bayer4>`: Applies ordered Bayer `2x2` or `4x4` pixel dithering across ramp transitions in local part coordinates.

### 4.1 Indented Primitives Inside a `part` Block

Each primitive supports constructive solid geometry (`op=union|smin|sub`), smooth blending radius (`k=2.0` for `op=smin`), a per-primitive material override (`ramp=<name>`), and an optional flat cel step (`step=<0..3>`):

| Primitive Syntax | Parameters and Description |
| :--- | :--- |
| `circle <cx>,<cy> r=<radius> [op=union\|smin\|sub] [k=<float>] [ramp=<name>] [step=<0..3>]` | Signed distance circle centered at `(cx, cy)` with radius `r`. |
| `box <cx>,<cy> <halfW>,<halfH> [r=<cornerR>] [op=...] [k=...] [ramp=...] [step=<0..3>]` | Axis-aligned box centered at `(cx, cy)` with half-extents `(halfW, halfH)` and optional corner rounding `r`. |
| `capsule <ax>,<ay> <bx>,<by> r=<radius> [op=...] [k=...] [ramp=...] [step=<0..3>]` | Swept sphere of radius `r` from `(ax, ay)` to `(bx, by)`. Ideal for limbs, tails, blades, horns, and wings. |
| `ring <cx>,<cy> r=<radius> [thick=<float>] [op=...] [k=...] [ramp=...] [step=<0..3>]` | Hollow ring centered at `(cx, cy)` with radius `r` and wall thickness `thick` (default `1.5`). |
| `poly <x1>,<y1> <x2>,<y2> <x3>,<y3> [...] [r=<roundR>] [op=...] [ramp=...] [step=<0..3>]` | Closed polygon with 3 or more vertices and optional corner rounding `r`. |
| `line <ax>,<ay> <bx>,<by> [thick=<float>] [op=...] [ramp=...] [step=<0..3>]` | Line segment from `(ax, ay)` to `(bx, by)` with thickness `thick` (default `1.5`). |
| `pixel <x>,<y> [w=<int>] [h=<int>] [step=<0..3>] [ramp=<name>]` | Exact pixel stamp at `(x, y)` of size `w x h` (default `1x1`) using ramp index `step` (`0`=shadow, `1`=base, `2`=light, `3`=specular; default `3`). |

### 4.2 SDF Smooth Blending Math (`op=smin`)

When `op=smin` is set with smoothing factor $k > 0$, two distance fields $d_1, d_2$ blend organically without hard seams:

$$h = \frac{\max(k - |d_1 - d_2|, 0)}{k}, \quad \text{smin}(d_1, d_2, k) = \min(d_1, d_2) - \frac{1}{4} h^2 k$$

---

## 5. Animation Tags (`tag`), Poses (`pose`), and Transform Math

In procedural mode, each `tag` block generates a sequence of frames by evaluating indented `pose` directives:

```text
tag <name> frames=<1..256> [duration=<ms>|fps=<num>] [loop=<loop|once|pingpong|reverse>]
  pose <part_name> [f=<all|idx|start..end>] [dx=<expr>] [dy=<expr>] [rot=<expr>] [scale=<s|sx,sy>] [squash=<expr>] [visible=<true|false>] [ease=<mode>]
```

### 5.1 Pose Channels and Expressions

- **Frame selector (`f=`)**: `f=all` (default), a single frame index within the tag (`f=2`), or an inclusive range (`f=0..3`).
- **Translation (`dx=`, `dy=`)**: Offset in pixels, snapped to integer coordinates (`math.Round`) so pixel details never shimmer between frames.
- **Rotation (`rot=`)**: Angle in degrees around the part's `pivot`.
- **Scale (`scale=`)**: Uniform (`scale=1.2`) or non-uniform (`scale=1.2,0.8`) scale factor.
- **Volume-Preserving Squash and Stretch (`squash=`)**: Stretches $Y$ by $1 + s$ and compresses $X$ by $\frac{1}{1 + s}$ so total pixel area stays constant during impacts and jumps:
  $$S_y = 1 + s, \quad S_x = \frac{1}{1 + s}$$
- **Visibility (`visible=`)**: Toggles part visibility (`true` or `false`) for the selected frame range.
- **Pose expressions (`<expr>`)**:
  - Constant: `dx=2.0`, `rot=-15`
  - Range interpolation: `0->8`, `-20->25`, `0.15->0.0` (interpolated across selected frames using `ease`)
  - Periodic wave over the tag cycle: `sin(2.5)`, `cos(1.5)`, `abs_sin(3.0)`
- **Easing modes (`ease=`)**:
  - `linear`: $f(t) = t$
  - `in_quad`: $f(t) = t^2$
  - `out_quad`: $f(t) = 1 - (1 - t)^2$
  - `in_out_cubic`: Smooth S-curve for idle breathing and hover loops
  - `elastic_out`: Springy overshoot for attacks and recoils

### 5.2 Non-Commutative 2D Matrix Transformation Order

Both the procedural SDF rasterizer (`Transform2D.GetGeoM`) and Ebitengine runtime drawing apply 2D affine matrices in strict order (`Pivot -> Scale/Squash -> Rotate -> World Translation`):

$$M = T(X + O_x, Y + O_y) \cdot R(\theta) \cdot S(S_x, S_y) \cdot T(-O_x, -O_y)$$

1. `m.Translate(-OriginX, -OriginY)`: Shift part pivot to $(0, 0)$.
2. `m.Scale(ScaleX, ScaleY)`: Apply scale and volume-preserving squash-and-stretch around the pivot.
3. `m.Rotate(Rotation)`: Rotate in radians around the pivot.
4. `m.Translate(OriginX+X, OriginY+Y)`: Translate back from pivot plus integer-snapped frame offset.

---

## 6. Procedural SDF Examples

### 6.1 Procedural Creature Example (`slime_familiar.sprite`)

```text
title "Slime Familiar"
type sprite
size 32x32
palette forest
outline #0D1712
light -0.5,-0.7

part shadow ramp=obsidian z=-5 pivot=16,28
  box 16,28 8,1.5 r=1.0 step=0

part body ramp=slime z=0 pivot=16,27 dither=bayer2
  circle 16,20 r=8.5
  box 16,24 9.0,4.0 r=2.5 op=smin k=2.5

part core ramp=gold z=2 pivot=16,21
  circle 16,21 r=3.0

part eyes ramp=obsidian z=5 pivot=16,19
  pixel 13,18 w=2 h=3 step=0
  pixel 18,18 w=2 h=3 step=0
  pixel 13,18 w=1 h=1 step=3 ramp=bone
  pixel 18,18 w=1 h=1 step=3 ramp=bone

tag idle frames=4 duration=150ms loop=loop
  pose body squash=sin(0.10)
  pose core dy=sin(1.0)
  pose eyes dy=sin(1.0)

tag jump frames=4 duration=95ms loop=once
  pose body f=0..0 squash=-0.18
  pose body f=1..2 dy=0->-7 squash=0.20->0.05 ease=out_quad
  pose body f=3..3 dy=-8 squash=-0.06
  pose core f=1..3 dy=0->-8 ease=out_quad
  pose eyes f=1..3 dy=0->-8 ease=out_quad
```

### 6.2 Seamless Tileset Example (`dungeon_brick.sprite`)

```text
title "Dungeon Brick Tiles"
type tileset
size 16x16
palette noir
outline none

part base ramp=obsidian z=0 dither=bayer2
  box 8,8 8,8 step=1

part bricks ramp=steel z=2
  box 4,4 3.5,3.0 r=0.5 step=1
  box 12,4 3.5,3.0 r=0.5 step=2
  box 8,12 7.0,3.0 r=0.5 step=1

part moss ramp=emerald z=4
  pixel 2,1 w=3 h=1 step=2
  pixel 11,9 w=2 h=1 step=1

tag tiles frames=4 duration=200ms loop=loop
  pose moss f=1..1 dx=2
  pose moss f=2..2 dy=3
  pose moss f=3..3 dx=-2 dy=2
```
