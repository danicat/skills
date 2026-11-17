---
name: ebitengineer
description: >
  Engineering architecture and best practices for building 2D games in Go using
  Ebitengine (v2). Covers modular game architecture, scene state machines,
  virtual resolution scaling, delta-time physics, zero-allocation draw loops,
  sprite sheet and AnimationController playback, 4-byte aligned 44.1 kHz stereo
  PCM audio, Kage shaders, and WebAssembly builds. Activate when building,
  optimizing, or debugging 2D games in Go, or compiling Ebitengine games to WebAssembly.
license: Apache-2.0
metadata:
  category: game-dev
  tags: "ebitengine, go, games, 2d, wasm, shaders"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.4.0"
  catalog: https://skills.danicat.dev
---

# Ebitengine 2D game development guide (`ebitengineer`)

Genre-agnostic engineering guidelines for building modular, high-performance, cross-platform 2D games (top-down, tactics, shmup, puzzle, isometric, and platformer) in Go using [Ebitengine v2](https://ebitengine.org/) (`github.com/hajimehoshi/ebiten/v2`).

---

## Trigger conditions

Activate this skill whenever:
- Designing or implementing 2D game architecture, scene flow, camera systems, or rendering pipelines in Go.
- Working with Ebitengine interfaces (`ebiten.Game`), state machines, input management, sprite animation controllers, audio streams, Kage shaders, or `ebiten/v2/text/v2` typography.
- Compiling games to native desktop and WebAssembly (`GOOS=js GOARCH=wasm`), optimizing cycle timing, synchronizing WASM audio, persisting saves, hosting on Cloud Run, or writing unit tests for Go game components.

---

## Companion skills

`ebitengineer` works alongside these focused skills when building a complete 2D game:

- **`vibe-game-developer` and `game-design`**: `vibe-game-developer` orchestrates the end-to-end build pipeline while `game-design` defines the Game Design Document (GDD), core loop, virtual resolution (`320x180`, `640x360`, `1280x720`, or `1920x1080`), state progression, and feel budgets. `ebitengineer` turns those specifications into decoupled Go packages under `internal/`.
- **`sprite-design`**: Supplies declarative `.sprite` files, binary `.aseprite` v1.3 containers, or normalized `.png` + `.json` sprite sheets at any resolution (retro pixel art like `32x32` and `64x64`, or native 2D HD like `256x256` and `512x512`). Pre-slice every grid cell once at boot (`NewGridSpriteSheet`) and drive playback with a zero-allocation `AnimationController` (`Update(dt)` in `Update()` and `Draw(screen, x, y, flipX)` in `Draw()`).
- **`procedural-sfx`, `procedural-music`, and `lyria`**: Shares a single `44100` Hz Ebitengine `audio.Context` across procedural `.sfx` cues, `.music` BGM scores, and `lyria` AI audio streams. Decode or synthesize all audio into **4-byte aligned** 16-bit little-endian stereo PCM byte slices (`len(pcm) &^ 3`) during boot, enforce per-cue SFX cooldowns in `Update()`, and seek BGM streams to 4-byte aligned offsets (`offset &^ 3`) on first user gesture in WebAssembly.
- **`godoctor`, `swarm-coding`, and `parallel`**: Use `godoctor` for Go static analysis, AST inspection, and build verification across desktop and WASM targets. When building multiple decoupled subsystems (`internal/physics`, `internal/camera`, `internal/ui`, `internal/tilemap`, `internal/ai`, `internal/save`), define package interfaces first and implement and unit-test each package independently.

---

## Core architecture and fail-fast engineering rules

### 1. Modular architecture (`internal/`)
Organize the codebase into modular subsystems under `internal/`. Never build monolithic single-file games.
- For the complete directory tree and package responsibilities, see [`references/project_structure.md`](references/project_structure.md).

### 2. Fail-fast asset embedding and validation (no silent fallbacks)
- **Zero-dependency embedding**: Embed all game assets (`.sprite`, `.aseprite`, `.png` sprite sheets, `.sfx` and `.music` scores, TTF/OTF fonts, Kage shaders) directly into the compiled Go binary using `embed.FS` (`internal/assets`).
- **No silent fallbacks**: Never ignore errors (`_ = err`), never substitute dummy `1x1` fallback textures when an asset fails to decode, and never silently clamp out-of-bounds tile or frame IDs. Always fail fast and return rich `fmt.Errorf` diagnostics during `Boot` initialization.
- **Mandatory binary format validation**: Always validate asset files using file identification tools (`file`, `mimetype`, or `http.DetectContentType` in Go) during asset ingestion. Misnamed or corrupt asset files cause decoding failures or black screens on WebAssembly.

### 3. Premultiplied alpha invariant (`color.RGBA` vs. `color.NRGBA`)
- In Go's `image/color` and Ebitengine, `color.RGBA` is **alpha-premultiplied**: every channel must satisfy $R \le A$, $G \le A$, $B \le A$.
- Never construct non-premultiplied literals like `color.RGBA{255, 0, 0, 100}` (where $R > A$). Use valid premultiplied `color.RGBA{100, 0, 0, 100}` or straight-alpha `color.NRGBA{255, 0, 0, 100}`.

### 4. Aspect ratio and virtual pixel canvas
- **16:9 widescreen priority**: Unless specified otherwise, target a **16:9 virtual resolution** (`320x180`, `640x360`, `1280x720`, `1920x1080`).
- **Virtual pixel canvas**: All entity physics, collision math, camera coordinates, Kage shader pixel units, and UI layouts operate strictly in virtual canvas coordinates.
- **Automatic multi-resolution scaling**: `Layout(outsideWidth, outsideHeight int)` returns constant virtual dimensions (`virtualWidth, virtualHeight`).

### 5. Cycle timing and frame synchronization
- **Target frame rate**: Standard target is **60 TPS** (`ebiten.SetTPS(60)`).
- **Delta-time integration**: Integrate movement, camera exponential decay, and timers using delta time ($dt = 1.0 / 60.0$ or measured frame delta) for consistent behavior across refresh rates.
- **Windowing and fullscreen toggle**: Support fullscreen toggling via `F11` or `Alt+Enter`:
```go
if inpututil.IsKeyJustPressed(ebiten.KeyF11) || (ebiten.IsKeyPressed(ebiten.KeyAlt) && inpututil.IsKeyJustPressed(ebiten.KeyEnter)) {
    ebiten.SetFullscreen(!ebiten.IsFullscreen())
}
```

---

## Sprite, audio, and WebAssembly runtime patterns

### 1. Zero-allocation sprite and animation playback
Whether rendering low-res pixel art (`32x32`, `64x64`) or high-res 2D HD sprites (`256x256`, `512x512`) from `sprite-design`, pre-slice all frames from the atlas once during `Boot` initialization and advance a zero-allocation `AnimationController` in `Update()`:

```go
// Pre-slice grid cells once at load time (never call SubImage inside Draw)
sheet, err := NewGridSpriteSheet(atlasImage, frameWidth, frameHeight)
if err != nil {
    return fmt.Errorf("boot: slice sprite sheet: %w", err)
}
ctrl, err := NewAnimationController(sheet)
if err != nil {
    return fmt.Errorf("boot: init animation controller: %w", err)
}
if err := ctrl.AddTag("idle", 0, 3, 150*time.Millisecond, LoopForward); err != nil {
    return err
}
if err := ctrl.Play("idle"); err != nil {
    return err
}
```
- **Pixel art vs. 2D HD filtering**: Use `ebiten.FilterNearest` when drawing pixel-art sprites or `1:1` native 2D HD frames so pixels stay crisp. Use `ebiten.FilterLinear` when scaling down high-resolution `256x256` or `512x512` 2D HD sprites onto a smaller gameplay canvas.

### 2. Unified `44.1 kHz` stereo PCM audio
Create a single `audio.NewContext(44100)` for the entire game process. Ebitengine requires all raw PCM streams to use **16-bit signed little-endian stereo PCM (4 bytes per sample frame: 2 bytes Left + 2 bytes Right)**:
- Always mask buffer lengths and seek offsets with `&^ 3` (`aligned := length &^ 3`) before passing them to `audio.NewInfiniteLoop`, `audio.NewInfiniteLoopWithIntro`, `ctx.NewPlayerFromBytes`, or `Seek()`.
- Pre-synthesize `.sfx` and `.music` scores to `[]byte` buffers during `Boot` initialization (never inside `Update()` or `Draw()`), and enforce a per-cue cooldown (such as `40ms` to `80ms`) on rapid SFX triggers to prevent voice stacking clipping.

### 3. Dual-target CLI build verification
Always verify both the test suite and the WebAssembly compilation target before shipping:

```bash
go test ./...
GOOS=js GOARCH=wasm go build -o /dev/null ./cmd/game
```

---

## Engine reference modules

Consult these reference guides for complete, zero-allocation, fail-fast Go implementations:

| Module | Reference File | Key Topics Covered |
| :--- | :--- | :--- |
| **Project structure** | [`references/project_structure.md`](references/project_structure.md) | Package tree and `internal/` subsystem responsibilities. |
| **Camera and game feel ("Juice")** | [`references/camera_and_juice.md`](references/camera_and_juice.md) | 2D `ebiten.GeoM` camera, exponential lerp, trauma screen shake, hitstop freeze frames, squash-and-stretch springs, `Transform2D` pivot matrix order, easing curves, and zero-alloc `ParticleSystem` pools. |
| **Kage shaders and `text/v2`** | [`references/shaders_and_text_v2.md`](references/shaders_and_text_v2.md) | Kage `//kage:unit pixels` shaders (2D lighting, CRT, hit-flash) and `ebiten/v2/text/v2` font loading and aligned layout. |
| **WASM audio and save storage** | [`references/wasm_audio_and_persistence.md`](references/wasm_audio_and_persistence.md) | 4-byte aligned (`&^ 3`) `44.1 kHz` stereo PCM playback, `SFXBank` cooldown throttling, WASM autoplay unlock `Seek()`, and build-tagged desktop vs. WASM save storage. |
| **UI and HUD system** | [`references/ui_and_hud.md`](references/ui_and_hud.md) | Premultiplied alpha invariant (`R <= A`), pre-sliced 9-slice panels, anchoring math, zero-alloc progress bars, and `text/v2` buttons. |
| **Physics and collision** | [`references/physics_and_collision.md`](references/physics_and_collision.md) | Genre-agnostic Circle and AABB overlap, axis-separated sweep resolution, spatial hash grids, and slope math. |
| **Tilemaps and levels** | [`references/tilemaps_and_levels.md`](references/tilemaps_and_levels.md) | Pre-sliced tileset validation, camera frustum culling, isometric projection, and 16-pipe bitmask autotiling. |
| **Input action mapping** | [`references/input_action_mapping.md`](references/input_action_mapping.md) | Rebindable action maps, radial analog deadzones, and zero-alloc gamepad polling. |
| **Entity management** | [`references/entity_management.md`](references/entity_management.md) | Pre-allocated slice pools, deferred deletion buffers, and Structure-of-Arrays (SoA) Light ECS. |
| **Pathfinding and AI** | [`references/pathfinding_and_ai.md`](references/pathfinding_and_ai.md) | Fail-fast A* grid pathfinding, steering behaviors (seek and arrive), and enemy decision FSM. |
| **Server and Cloud Run** | [`references/server_architecture.md`](references/server_architecture.md) | WebAssembly build, multi-stage Dockerfile, hardened HTTP server, and Cloud Run leaderboard REST API. |

---

## Game state machine and scene flow

### Finite state machine (FSM) lifecycle
Model all scenes using a `State` interface with strict lifecycle hooks (`Enter() error`, `Update(dt float64) error`, `Draw(screen *ebiten.Image)`, `Exit() error`).

### Standard scene progression
```text
Boot (Logo & Asset Preload) -> Intro -> Title Screen -> Game Play -> Game Win / Game Over -> Title Screen
```

### Transition cleanliness (no leaks)
Upon `Exit()`, every state **must**:
- Stop or fade out BGM/SFX channels belonging to that scene.
- Flush active particle emitters, animations, hitstop timers, and camera trauma.
- Reset transient input buffers so button presses do not bleed into the next state.

### Attract and demo mode (arcade style)
1. **Idle timeout**: On `Title Screen`, if no input arrives after a timeout (such as `10s`), transition to `Demo Mode` (autonomous AI/CPU plays the game).
2. **Instant interrupt**: Any user input in `Demo Mode` interrupts execution immediately back to `Title Screen`.
3. **Alternating flow**: Consecutive `Title Screen` idle timeouts alternate between launching `Demo Mode` and re-playing `Intro`.

---

## WebAssembly (WASM), shaders, and typography rules

- **Audio late-sync (4-byte PCM alignment)**: Browser WebAudio stays locked until the first user gesture. Track elapsed time during silent load and `Seek()` to a **4-byte aligned** stereo PCM byte offset (`((samples * 4) % loopLengthBytes) &^ 3`) on first interaction. See [`references/wasm_audio_and_persistence.md`](references/wasm_audio_and_persistence.md).
- **Custom typography (`ebiten/v2/text/v2` only)**: Never use `ebitenutil.DebugPrint` for game UI and never use deprecated `ebiten/v2/text` v1. Always load TTF/OTF fonts via `text.NewGoTextFaceSource`, `text.GoTextFace`, and `text.Draw` from `github.com/hajimehoshi/ebiten/v2/text/v2`. See [`references/shaders_and_text_v2.md`](references/shaders_and_text_v2.md).
- **Kage shaders (`//kage:unit pixels`)**: Always include `//kage:unit pixels` in Kage shaders and pre-allocate `ebiten.DrawRectShaderOptions` and uniform maps at load time. See [`references/shaders_and_text_v2.md`](references/shaders_and_text_v2.md).
- **Build-tagged save persistence**: Implement separate `//go:build !js` (atomic file write in `os.UserConfigDir()`) and `//go:build js && wasm` (`window.localStorage`) storage backends behind a common fail-fast interface. See [`references/wasm_audio_and_persistence.md`](references/wasm_audio_and_persistence.md).

---

## Unit testing and performance rules

1. **Zero allocations in `Draw()`**: Never call `ebiten.NewImage()`, `SubImage()`, `ebiten.NewShader()`, or allocate slices or maps inside `Draw()`. Pre-allocate all `ebiten.DrawImageOptions`, `text.DrawOptions`, `Uniforms`, and `SubImage` frame slices during initialization.
2. **Decouple logic and render**: Keep all state mutation strictly inside `Update()`. `Draw()` must be a read-only projection of current game state.
3. **Unit test coverage**: Write deterministic unit tests for state transitions, collision and spatial hash math, camera lerp and trauma decay, 4-byte PCM alignment, A* pathfinding, and save serialization.
