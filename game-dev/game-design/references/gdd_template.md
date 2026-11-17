# Game Design Document (GDD) template

> **Game Title**: [Insert Title]
> **Target 2D Genre**: [Side-Scroller Action/Platformer | Top-Down RPG/Adventure | Roguelike/Bullet-Heaven | Puzzle | Shmup | Turn-Based Tactics | Isometric 2:1 Strategy | Visual Novel]
> **Camera Projection & Spatial Model**: [2D Side-Profile | 3/4 Top-Down Orthographic | Isometric 2:1 (`26.565 deg`) | Front-Facing Orthographic]
> **Simulation Model**: [Real-Time Continuous (`60 TPS` fixed timestep) | Turn-Based Phases | Discrete Grid-Step | Event/Dialogue-Driven]
> **Target Platform**: Desktop (macOS/Windows/Linux) & WebAssembly (Browser / Hosted Server)
> **Virtual Canvas & Aspect Ratio**: [16:9 Widescreen (`1280x720` for 2D HD/UI, `640x360` balanced, or `320x180` retro pixel art)]
> **Author / Lead Designer**: [User Name / Agent]

## Executive summary and elevator pitch

- **Elevator Pitch**: [1 to 2 sentence hook describing the core player fantasy, 2D genre, and primary mechanic twist]
- **Core Inspiration**: [e.g., *Celeste*, *Hades*, *Vampire Survivors*, *Into the Breach*, *Slay the Spire*, *Streets of Rage*, *Puyo Puyo*]
- **Target Mood & Pacing**: [e.g., Fast-paced arcade action, tense tactical planning, relaxing puzzle flow, atmospheric dungeon exploration]

## Core gameplay loop, simulation, and mechanics

- **Primary Gameplay Loop**: [Step-by-step cycle: Player Decision/Action -> Systemic Challenge -> Feedback/Progression]
- **Spatial & Simulation Rules**:
  - **Movement & Interaction Topology**: [e.g., Side-view platforming with variable jump height and coyote time, 8-way top-down movement, isometric diamond grid stepping, or pointer drag-and-drop]
  - **Player Abilities & Actions**: [e.g., Melee combo and dash, directional spell cast, auto-fire weapon upgrades, unit tile command, puzzle cluster rotation]
  - **Systemic Challenges & Enemies**: [e.g., Patrol and boss patterns, swarming enemy waves, turn-based enemy intent telegraphs, move count or timer pressure]
- **Win & Loss Conditions**:
  - **Win Condition**: [e.g., Clear stage waves and defeat boss, solve all grid targets within par moves, capture command point, reach ending]
  - **Loss Condition**: [e.g., Player HP reaches 0, squad defeated, board locked with no valid moves, timer expires]

## Controls and input mapping scheme

- **Primary Input Devices**: [Keyboard, Mouse/Pointer, Gamepad, Touch]
- **Default Control Scheme**:

| Logical Action | Keyboard / Mouse | Gamepad Button | Touch Gesture |
| :--- | :--- | :--- | :--- |
| `ActionNavigate / Move` | `WASD` / `Arrows` / Mouse Cursor | Left Stick / D-Pad | Virtual Stick / Drag |
| `ActionPrimary / Confirm` | `Space` / `Z` / `Enter` / Left Click | Button South (`A` / `Cross`) | Tap Target / Action Button |
| `ActionSecondary / Cancel` | `Shift` / `X` / Right Click | Button East (`B` / `Circle`) | Two-Finger Tap / Secondary Button |
| `ActionInspect / Special` | `E` / `C` / `Tab` / Middle Click | Button West/North (`X` / `Y`) | Long Press |
| `ActionPause` | `Escape` / `P` | Start / Options | Pause Icon Button |

## Visual art direction and sprite pipeline (`sprite-design` + `nano-banana`)

- **Aesthetic Direction & Color Palette**: [e.g., Hand-drawn 2D HD cel-shaded arcade art, or 16-bit pixel art using a 4-step material ramp (`Shadow -> Base -> Light -> Specular`)]
- **Sprite Resolution Tier**:
  - `[ ]` **Native 2D HD (`256x256` or `512x512` per frame)**: Smooth outlines and full-resolution detail.
  - `[ ]` **Retro Pixel Art (`32x32` or `64x64` per frame)**: Crisp pixel grid with binary alpha edges.
- **Selected Visual Pipeline Mode**: `[Path A: Two-Step AI + normalize | Path B: Pure-Code .sprite DSL | Path C: Hybrid Pipeline]`
  - **Two-Step AI Assets (`nano-banana` + `sprite-design` `normalize`)**: [e.g., Hero turnaround sheet -> `4x4` chroma grid normalized to `.sprite`, `.aseprite`, and `.png`+`.json`, boss sprites, title art, parallax backgrounds, portraits]
  - **Pure-Code `.sprite` DSL Assets (`sprite-design`)**: [e.g., Seamless level tilesets, geometric enemies, projectiles, pickups, and props authored in `.sprite` SDF/pixel DSL]
- **Entity Animation Motion Tags (`AnimationController`)**:
  - **Player / Primary Unit**: [e.g., `idle`, `walk`, `run`, `jump`, `fall`, `attack`, `hit`, `death`]
  - **Enemies / Interactive Pieces**: [e.g., `idle`, `move`, `attack`, `hit`, `death` or `idle`, `hover`, `match`, `clear`]

## Audio, music, and cutscene pipeline (`procedural-sfx`, `procedural-music`, `lyria`, `gemini-omni`)

- **Selected Audio Pipeline Mode**: `[Pure-Code Procedural (.sfx + .music) | Hybrid (.sfx + lyria) | Full AI Music + Procedural SFX]`
- **Sound Effects (`procedural-sfx` `.sfx` DSL)**:
  - **Gameplay / Combat**: [e.g., `jump_arcade.sfx`, `laser_arcade.sfx`, `sword_clash.sfx`, `hit_punch.sfx`, `explosion_deep.sfx`]
  - **Pickups & Progression**: [e.g., `coin_pickup.sfx`, `gem_shimmer.sfx`, `powerup_fanfare.sfx`]
  - **UI & Menus**: [e.g., `ui_select.sfx`, `ui_confirm.sfx`, `ui_error.sfx`]
- **Background Music (`procedural-music` `.music` DSL or `lyria`)**:
  - **Tempo, Time Signature & Key**: [e.g., `tempo allegro 138`, `4/4`, `C Minor`]
  - **Synthesis Engine & Palette**:
    - `[ ]` **`procedural-music` Default (Pure-Go SEGA YM2612 4-Op FM + SN76489 PSG)**: Zero-asset 16-bit stereo PCM soundtrack (`8 to 12+` channels with sub-bass/bass anchored in `C1` to `C2`).
    - `[ ]` **`procedural-music` Apple (`synth apple` / `-apple` CoreAudio)**: Real sampled instruments via macOS `gs_instruments.dls`.
    - `[ ]` **`lyria` AI Studio Tracks**: 44.1 kHz stereo tracks (`lyria-3.5`, `lyria-3-pro-preview`, or `lyria-3-clip-preview`).
- **Cutscenes and Title Animations (`gemini-omni`)**:
  - **Video Clips**: `[None | gemini-omni-1.2-flash 3s to 15s intro/outro or boss transitions with synchronized audio]`

## Scene flow and UI/HUD layout

- **Scene State Machine**: `Boot` -> `Title / Main Menu` -> `Gameplay / Stage` -> `Overlay (Pause / Inventory / Tactical Map / Dialogue)` -> `Victory / Game Over`
- **HUD & UI Regions (`text/v2` + Ebitengine UI)**:
  - **Top-Left**: [e.g., Player HP bar, shield/mana gauge, active status icons]
  - **Top-Right**: [e.g., Score, wave/turn counter, stage timer, minimap]
  - **Bottom / Action Area**: [e.g., Action bar, card hand, combo meter, or dialogue box]

## Technical scope and Ebitengine architecture (`ebitengineer`)

- **Core Runtime Subsystems**:
  - **Coordinate & Collision System**: [e.g., AABB tilemap sweep (platformer/top-down), Uniform Spatial Hash (bullet-heaven/shmup), Axial/Diamond Grid Coordinates (tactics/isometric/puzzle), or UI Hit-Testing Rects (deckbuilder/VN)]
  - **Zero-Allocation Hot Loop**: Pre-allocated entity/particle slices and reused `ebiten.DrawImageOptions` / 4-byte aligned audio buffers (`len(pcm) &^ 3`) inside `Update()` and `Draw()`
  - **Save Persistence & Backend**: [None | Build-tagged atomic JSON in `os.UserConfigDir()` (desktop) + `window.localStorage` (WASM) | Cloud Run REST leaderboard]
  - **Verification**: `go test ./...` and headless + `GOOS=js GOARCH=wasm` browser playtest on `http://localhost:8080`
