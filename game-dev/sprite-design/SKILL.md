---
name: sprite-design
description: >
  Guide and .sprite engine for 2D game sprites, tilesets, and frame animations
  in Ebitengine. Covers the two-step AI character sheet to chroma-key grid
  pipeline with nano-banana, normalization into .sprite, .aseprite, .png, and
  .json containers, procedural SDF sprites, visual QA checks, and zero-allocation
  AnimationController state machines.
license: Apache-2.0
metadata:
  category: game-dev
  tags: "sprites, animation, pixel-art, tilesets, aseprite, sdf"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.4.0"
  catalog: https://skills.danicat.dev
---

# 2D sprite design, normalization, and frame animation

`sprite-design` turns character designs and procedural rules into game-ready 2D sprite containers (`.sprite`, `.aseprite`, `.png`, and `.json`) and drives them at 60 FPS in Ebitengine without heap allocations in `Draw()`.

- **`.sprite` container and procedural DSL spec**: [`references/dsl-reference.md`](references/dsl-reference.md)
- **Binary Aseprite and `.gpl` palette spec**: [`references/aseprite_format.md`](references/aseprite_format.md)
- **Sample procedural sprite**: [`scripts/slime_familiar.sprite`](scripts/slime_familiar.sprite)

---

## Companion skills

| Skill | Role in the sprite pipeline |
| :--- | :--- |
| **`vibe-game-developer`** | Orchestrates end-to-end game builds and delegates character and tileset production to `sprite-design`. |
| **`game-design`** | Defines player mechanics, animation tag budgets, hitbox timing, and camera projection before sprite creation. |
| **`nano-banana`** | Generates the Step 1 character reference sheet and raw Step 2 `4x4` chroma-key grids for `normalize`. |
| **`ebitengineer`** | Integrates `GridSpriteSheet` and `AnimationController` into the fixed 60 TPS `Update()` loop and camera `GeoM` pipeline. |

---

## Available scripts

Run CLI commands from the skill root (`go run ./scripts <command> ...`) or change into `scripts/` when working inside the Go module:

- `scripts/sprite.go`: `.sprite` parser (`LoadSpriteFile`, `ParseSpriteDSL`), procedural SDF compiler (`CompileSprite`), sheet normalizer (`NormalizeMultiSpriteSheets`), visual QA validator (`ValidateSprite`), and Ebitengine `GridSpriteSheet` / `AnimationController`.
- `scripts/aseprite.go`: Binary `.aseprite` v1.3 importer/exporter (`ImportAseprite`, `ExportAseprite`), PNG/JSON exporter (`ExportPNGSheet`), and palette ramp extractor (`ExtractPaletteRamps`).
- `scripts/play.go`: CLI runner (`validate`, `normalize`, `export`, `extract-palette`, `inspect-json`, `synth-json`).
- `scripts/sprite_test.go`: Unit tests covering premultiplied RGBA math, palettes, SDF primitives, container round-trips, and controller lifecycles.
- `scripts/slime_familiar.sprite`: Sample procedural SDF sprite for testing zero-argument `go run . validate`.

```bash
# Run unit tests inside scripts/
(cd scripts && go test -v ./...)

# Validate .sprite, .aseprite, or .png assets
go run ./scripts validate scripts/slime_familiar.sprite

# Normalize one or more raw AI grids into .png, .sprite, .json, .aseprite, preview, and GIFs
go run ./scripts normalize -cols 4 -rows 4 -center=true -ground=true -pad 8 \
  -tag idle:0:3:100:pingpong -tag walk:4:7:100:loop \
  -out hero.png -sprite hero.sprite -json hero.json -aseprite hero.aseprite \
  -preview hero_preview.png -gif-dir gifs raw_grid.png

# Export a .sprite file (container or procedural SDF) to .aseprite, .png, .json, preview, and GIFs
go run ./scripts export -png out.png -json out.json -aseprite out.aseprite \
  -preview out_preview.png -gif-dir gifs -scale 4 scripts/slime_familiar.sprite

# Extract 4-step material ramps from a character sheet PNG
go run ./scripts extract-palette -ramps 4 character_sheet.png

# Emit single-line JSON inspection or synthesis reports
go run ./scripts inspect-json scripts/slime_familiar.sprite
go run ./scripts synth-json -png out.png scripts/slime_familiar.sprite
```

---

## Two-step AI sprite generation pipeline

Generating a full sprite sheet in a single prompt fails when an image model tries to invent character design and maintain frame consistency at once. Split character design (Step 1) from animation grid generation and normalization (Step 2).

### Step 0: Confirm motions, projection, resolution, and path

Before creating an asset, confirm any detail missing from the request:

1. **Animation tags (`tag`)**:
   - Side-scroller or platformer: `idle`, `walk`, `run`, `jump` (with mid-air apex pose), `fall`, `crouch`, `attack`, `hit`, `death`.
   - Top-down RPG or twin-stick: `idle`, `walk`, `run`, `interact`, `attack`, `cast`, `hit`, `ko`.
   - Isometric `2:1` tactics: `idle`, `move`, `action`, `selected`, `damaged` across `SE`, `SW`, `NE`, `NW`.
   - Puzzle, card, or arcade shooter: `idle`, `hover` or `bank`, `activate` or `boost`, `combo_glow`, `burst`.
2. **Camera projection**: `2D side-profile`, `3/4 top-down`, `isometric 2:1 (26.565 deg)`, or `front-facing ortho`.
3. **Target frame resolution**: `256x256` Native 2D HD (default), `128x128` compact HD, or `64x64` / `32x32` pixel art (`-fw 64 -fh 64` or `-fw 32 -fh 32`).
4. **Production path**: Path A (AI character sheet plus `4x4` grid normalization) for expressive heroes and bosses; Path B (procedural `.sprite` DSL) for slimes, projectiles, pickups, and seamless tilesets.

### Step 1: Generate the character reference sheet (`nano-banana`)

Use `nano-banana` (`banana.py`) to build a character turnaround sheet before generating animation grids:

```bash
uv run path/to/nano-banana/scripts/banana.py \
  -p "2D game character reference sheet of a black anime cat hero, 1:2 head-to-body ratio, 2D side-profile gameplay angle, clear limb and tail separation, printed 4-step color swatch bar" \
  -m "nano-banana-2.1" -r "2K" -a "1:1" -f "character_sheet.png"
```

Include four traits in every Step 1 prompt:
1. **`1:2` to `1:3` head-to-body ratio**: Keeps eyes, silhouettes, and readability crisp at both HD and `64x64` / `32x32` scales.
2. **Exact gameplay projection**: Match the game camera angle (`side-profile`, `3/4 top-down`, `isometric 2:1`, or `front-facing`).
3. **Clear limb and silhouette separation**: Keep arms, tails, capes, and weapons slightly away from the torso.
4. **Printed 4-step color swatch bar**: Lock exact `Shadow -> Base -> Light -> Specular` tones for Step 2 consistency.

If image generation fails due to missing credentials or auth errors, stop and report the exact remediation command. Never substitute placeholder squares or bypass credentials.

### Step 2: Generate the `4x4` chroma-key grid and normalize

Pass `character_sheet.png` via `-i` to `nano-banana` to generate uniform `4x4` animation grids (`1024x1024`) on flat `#00FF00` bright green or `#FF00FF` magenta with no grid lines, borders, or text labels. For eight motions (`32` frames), generate two `4x4` grids (`4` motions each) and pass both paths to `normalize`.

```bash
uv run path/to/nano-banana/scripts/banana.py \
  -p "Uniform 4x4 2D sprite sheet grid on a flat #00FF00 chroma-key background, no grid lines or labels, at least 15% empty #00FF00 margin inside every cell. Row 1: 4-frame idle breathing. Row 2: 4-frame walk cycle. Row 3: 4-frame run cycle. Row 4: 4-frame jump arc (crouch anticipation, upward launch, rising ascent, horizontal mid-air apex suspension)." \
  -i "character_sheet.png" -m "nano-banana-2.1" -r "1K" -a "1:1" -f "raw_grid_part1.png"
```

Enforce two rules in every Step 2 prompt:
- **15% empty cell margin**: Leave at least `15%` empty `#00FF00` padding on all four sides of every character cell so tails, ears, and weapons never cross row boundaries.
- **Complete 4-frame jump arc**: Specify `crouch anticipation`, `upward launch`, `rising ascent`, and `horizontal mid-air apex` so `jump` transitions smoothly into `fall`.

Run `go run ./scripts normalize` to split gutters, prune disconnected border artifacts (`findMainBodyAndFullBBox`), unmix chroma fringes into premultiplied RGBA ($R, G, B \le A$), center horizontally, ground non-airborne frames, and emit `.png`, `.sprite`, `.json`, `.aseprite`, preview PNG, and per-tag GIFs:

```bash
# Native 256x256 2D HD (omit -fw and -fh to preserve native w/cols x h/rows cell resolution)
go run ./scripts normalize -cols 4 -rows 4 -center=true -ground=true -pad 8 \
  -tag idle:0:3:100:pingpong \
  -tag walk:4:7:100:loop \
  -tag run:8:11:100:loop:9 \
  -tag jump:12:15:100:once \
  -tag fall:16:19:100:loop \
  -tag crouch:20:23:100:once \
  -tag sleep:24:27:100:pingpong \
  -tag attack:28:31:100:once \
  -out hero_cat.png -sprite hero_cat.sprite -json hero_cat.json -aseprite hero_cat.aseprite \
  -preview hero_preview.png -gif-dir gifs raw_grid_part1.png raw_grid_part2.png

# Retro 64x64 pixel art (pass explicit -fw and -fh to downsample cleanly)
go run ./scripts normalize -fw 64 -fh 64 -cols 4 -rows 4 -center=true -ground=true -pad 3 \
  -tag idle:0:3:100:pingpong -tag walk:4:7:100:loop -tag run:8:11:100:loop:9 -tag jump:12:15:100:once \
  -out hero_64.png -sprite hero_64.sprite -json hero_64.json -aseprite hero_64.aseprite \
  -preview hero_64_preview.png -gif-dir gifs_64 -scale 4 raw_grid_part1.png
```

Always generate `-preview` and `-gif-dir` and inspect the exported images before integrating the sprite into a game to catch baseline drift, cropped limbs, or cell bleed.

---

## The `.sprite` format: sheet containers and procedural SDF

### Sheet-backed container (`sheet "..."`)

Written automatically by `normalize` or edited by hand, a container `.sprite` links an atlas `.png` or `.aseprite` to its frame size, grid layout, `fps` or `duration`, and tag ranges (including optional lead-in `once` frames like `tag run 8 once, 9..11 loop`):

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

### Procedural SDF and pixel-art definition (`part ...`)

When a `.sprite` script omits `sheet` and defines Z-ordered `part` blocks instead, `CompileSprite` evaluates 2D Signed Distance Fields (`circle`, `box`, `capsule`, `ring`, `poly`, `line`, `pixel`), shades normals across 4-step material ramps, adds a 1px outline for sprites (none for seamless `type tileset`), and animates parts via `pose` transforms (`dx`, `dy`, `rot`, `scale`, `squash`, `visible`, `ease`):

```text
title "Star Pickup"
type sprite
size 24x24
palette snes
outline #141020
light -0.5,-0.7
fps 10

part body ramp=gold z=0 pivot=12,12 dither=bayer2
  circle 12,12 r=6.5
  ring 12,12 r=8.0 thick=1.5 op=smin k=1.5
  pixel 10,9 w=2 h=2 step=3 ramp=bone

tag spin frames=4 loop=loop
  pose body dy=sin(1.5) squash=cos(0.12)
```

---

## Five visual QA checks (`ValidateSprite`)

1. **Premultiplied alpha (`R, G, B <= A`)**: Every pixel in every frame and `SheetRGBA` must pass `ValidatePremultipliedRGBA` to prevent bright blending halos.
2. **Bounding-box fill ratio**: `type sprite` must occupy `8.0%` to `92.0%` of the frame area; `type tileset` must occupy `50.0%` to `100.0%`.
3. **Center-of-mass stability**: Horizontal center of mass across frames must remain within `18%` to `82%` of frame width so `flipX` mirrors naturally without shifting position.
4. **Shading contrast**: Opaque pixels must span at least `3` distinct luminance buckets (out of `16` Rec. 601 quantized levels).
5. **Tag bounds and timing**: Every tag must satisfy `0 <= FromFrame <= ToFrame < TotalFrames` with positive `DurationMs`.

---

## Zero-allocation Ebitengine integration

### Option A: Load `.sprite` directly (`LoadSpriteFile` -> `ToEbitenController`)

Both container and procedural `.sprite` files compile into an `AnimationController` at boot with checked fail-fast transitions and `OnComplete` callbacks for one-shot actions (`attack`, `hurt`, `jump`):

```go
func NewActor(spritePath string) (*Actor, error) {
	spec, err := LoadSpriteFile(spritePath)
	if err != nil {
		return nil, err
	}
	compiled, err := CompileSprite(spec)
	if err != nil {
		return nil, err
	}
	ctrl, err := compiled.ToEbitenController()
	if err != nil {
		return nil, err
	}
	ctrl.OnComplete = func(tagName string) {
		if tagName == "attack" {
			if err := ctrl.Play("idle"); err != nil {
				log.Printf("sprite: return to idle: %v", err)
			}
		}
	}
	if err := ctrl.Play("idle"); err != nil {
		return nil, fmt.Errorf("play initial idle tag: %w", err)
	}
	return &Actor{X: 120, Y: 180, Anim: ctrl}, nil
}

func (a *Actor) Update() error {
	a.Anim.Update(time.Second / 60)
	return nil
}

func (a *Actor) Draw(screen *ebiten.Image) {
	a.Anim.Draw(screen, a.X, a.Y, a.FacingLeft)
}
```

### Option B: Embedded PNG atlas (`NewGridSpriteSheet`)

When embedding a normalized `.png` atlas via `//go:embed`, slice all cells once at startup so `Draw()` never calls `SubImage` or allocates `ebiten.DrawImageOptions` on the heap:

```go
sheet, err := NewGridSpriteSheet(atlasImage, 256, 256)
if err != nil {
	return nil, err
}
ctrl := NewAnimationController(sheet)
if err := ctrl.AddTag("idle", 0, 3, 100*time.Millisecond, LoopPingPong); err != nil {
	return nil, err
}
if err := ctrl.AddTagWithIntro("run", 8, 9, 11, 100*time.Millisecond, LoopForward); err != nil {
	return nil, err
}
if err := ctrl.AddTag("attack", 28, 31, 60*time.Millisecond, LoopOnce); err != nil {
	return nil, err
}
if err := ctrl.Play("idle"); err != nil {
	return nil, fmt.Errorf("play initial idle tag: %w", err)
}
```
