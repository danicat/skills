# Ebitengine Project Structure & Package Reference

A clean, modular Go game project layout keeps dependencies decoupled across any 2D genre (top-down, tactics, shmup, puzzle, isometric, or platformer), prevents monolithic single-file codebases, and compiles cleanly to both native desktop and WebAssembly (`GOOS=js GOARCH=wasm`).

---

## Recommended Directory Tree

```text
mygame/
├── cmd/
│   ├── game/
│   │   └── main.go               # Desktop/WASM entrypoint (window config & ebiten.RunGame)
│   └── server/
│       └── main.go               # HTTP server for WASM static files & High Score API
├── internal/
│   ├── game/
│   │   └── game.go               # ebiten.Game implementation & top-level game loop
│   ├── state/
│   │   ├── machine.go            # Finite State Machine (FSM) manager
│   │   ├── state.go              # State interface definitions (Enter, Update, Draw, Exit)
│   │   ├── boot.go               # Company Logo / Fail-fast asset preloader state
│   │   ├── intro.go              # Cinematic Intro state
│   │   ├── title.go              # Main Title Screen state
│   │   ├── play.go               # Active Gameplay state
│   │   ├── win.go                # Victory state
│   │   ├── gameover.go           # Game Over state
│   │   └── demo.go               # Arcade CPU Attract Mode state
│   ├── entity/
│   │   ├── manager.go            # Pre-allocated slice pool or Light ECS
│   │   ├── player.go             # Player entity & AnimationController state
│   │   └── enemy.go              # Enemy AI & steering/pathfinding
│   ├── input/
│   │   └── input.go              # Action mapping (Keyboard, Gamepad, Mouse, Touch)
│   ├── audio/
│   │   └── audio.go              # 44.1 kHz stereo PCM player, SFX cooldowns, & WASM late-sync
│   ├── camera/
│   │   └── camera.go             # GeoM viewport, exponential lerp, trauma shake, hitstop
│   ├── physics/
│   │   └── collision.go          # Circle/AABB collision & spatial hash grid
│   ├── render/
│   │   ├── sprite.go             # GridSpriteSheet & zero-alloc AnimationController
│   │   └── shaders.go            # Kage shaders (//kage:unit pixels) & post-processing
│   ├── save/
│   │   ├── storage.go            # Shared save contract & JSON validation
│   │   ├── storage_desktop.go    # //go:build !js atomic file persistence
│   │   └── storage_wasm.go       # //go:build js && wasm localStorage persistence
│   ├── ui/
│   │   ├── font.go               # ebiten/v2/text/v2 typography (zero debug prints)
│   │   └── widgets.go            # 9-slice panels, anchored layout, progress bars
│   └── assets/
│       └── assets.go             # Fail-fast embedded assets (.sprite, .aseprite, .png, .sfx, .music, .ttf, .kage)
├── web/
│   ├── index.html                # WASM web page wrapper
│   └── wasm_exec.js              # Go WebAssembly JS glue
├── go.mod
└── go.sum
```

---

## Package Responsibilities

- **`cmd/game`**: Entrypoint for native desktop (`go run ./cmd/game`) and WebAssembly builds (`GOOS=js GOARCH=wasm go build ./cmd/game`).
- **`cmd/server`**: Entrypoint for hosting WASM builds and High Score REST API endpoints.
- **`internal/game`**: Implements `ebiten.Game` (`Update`, `Draw`, `Layout`). Delegates lifecycle updates to `internal/state` and propagates errors visibly to stdout/stderr.
- **`internal/state`**: Manages state transitions and scene lifecycles. Ensures audio, particles, and camera trauma reset cleanly upon scene exit.
- **`internal/input`**: Abstracts raw keys, gamepad buttons/axes, mouse, and touch events into rebindable game action intents.
- **`internal/audio`**: Manages a single 44,100 Hz `audio.Context` shared across `procedural-music` (`.music`), `procedural-sfx` (`.sfx`), and `lyria` streams, enforcing 4-byte stereo PCM alignment (`&^ 3`), SFX cooldowns, and WASM late-touch `Seek()` synchronization.
- **`internal/camera`**: Manages world-to-screen `ebiten.GeoM` transforms, frame-rate independent exponential damping, trauma screen shake, hitstop, and spring squash-and-stretch.
- **`internal/render`**: Houses `sprite-design` `GridSpriteSheet` and `AnimationController` playback (supporting both pixel-art and 2D HD resolutions) alongside Kage shaders (`//kage:unit pixels`) for lighting, hit-flash, and CRT effects.
- **`internal/save`**: Build-tagged fail-fast save persistence (`os.UserConfigDir()` on desktop, `localStorage` on WASM).
- **`internal/ui`**: Renders HUD components with premultiplied `color.RGBA` and `github.com/hajimehoshi/ebiten/v2/text/v2`.
- **`internal/assets`**: Uses `//go:embed` to package sprites (`.sprite`, `.aseprite`, `.png`+`.json`), audio scripts/streams (`.sfx`, `.music`, `.wav`), TTF/OTF fonts, and Kage shaders into the Go binary, failing fast with `fmt.Errorf` if any asset fails validation or decoding.
