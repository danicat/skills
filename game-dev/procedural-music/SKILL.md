---
name: procedural-music
description: >
  Pure-code procedural music composition guide and .music DSL for polyphonic
  BGM in Ebitengine. Compiles 4-byte aligned 16-bit 44.1 kHz stereo PCM
  soundtracks via a pure-Go SEGA Mega Drive YM2612 4-op FM + PolyBLEP SN76489
  PSG synth or macOS CoreAudio (-apple gs_instruments.dls), with music-theory
  validation.
license: Apache-2.0
metadata:
  category: game-dev
  tags: "bgm, music, ym2612, chiptune, synthesis, ebitengine"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.4.0"
  catalog: https://skills.danicat.dev
---

# Procedural music: Original composition guide and dual-engine DSL

`procedural-music` compiles readable `.music` scores into 16-bit `44.1 kHz` stereo PCM soundtracks in memory using either of two engines:

1. **Default pure-Go (`default`, no `-apple` flag)**: SEGA Mega Drive **YM2612 (OPN2)** 4-operator FM + band-limited **PolyBLEP SN76489 PSG** + exponential-decay percussion with zero external assets or OS dependencies.
2. **Apple Real Instruments (`-apple` flag on macOS)**: Native `AudioToolbox` CoreAudio renderer backed by Apple's built-in Roland GS / General MIDI bank (`gs_instruments.dls`).

- **Full `.music` DSL grammar, attributes, and tie syntax**: [`references/dsl_spec.md`](references/dsl_spec.md)
- **Music theory, arranging, and 16-bit study archetypes**: [`references/music_theory_and_arranging.md`](references/music_theory_and_arranging.md)

Compose original soundtracks with bespoke palettes instead of stamping templates:
- Match instrumentation to setting (`8` to `12+` independent channels, `30s` to `150s+` for full BGM loops).
- Tie sustained notes across barlines with `~` (`C3:1~1`, `F5:8~ | :16`) while keeping syncopated stabs crisp with `R:16` release gaps.
- Anchor sub-bass in `C1` to `C2` (`32 Hz` to `130 Hz`) so `50%` to `75%` of spectral energy stays below `260 Hz`.

---

## Companion skills

| Skill | When to pair it with `procedural-music` |
| :--- | :--- |
| **`lyria`** | Choose `procedural-music` for sample-exact gapless loops, tiny `5 KB` to `20 KB` text scores, pure-Go WebAssembly builds, and isolated stem control. Choose `lyria` for AI-generated orchestral, vocal, or recorded ambient stems. |
| **`procedural-sfx`** | Share one `44,100 Hz` `audio.Context` across `.music` loops and `.sfx` cues; keeping BGM bass below `260 Hz` leaves mid/high headroom for SFX. |
| **`vibe-game-developer` & `game-design`** | Assign each scene state (title, stage, boss, fanfare, game over) its own tempo, mode, palette, and looped vs. one-off playback mode. |
| **`ebitengineer`** | Embed `.music` scores via `//go:embed`, pre-compile PCM at startup (never inside `Update()` or `Draw()`), and mask lengths/offsets with `&^ 3`. |

---

## Available scripts and reference scores

- `scripts/sound.go`: DSL lexer/parser (`ParseDSL`, `CompileDSL`, `LoadDSLFile`), synth engine (`SynthesizeScore`, `SynthesizeScoreWithStems`), theory checker (`ValidateScoreTheory`, `ValidateProductionBGM`), DSP helpers (`SliceLoopPCM`, `ApplyLowPassFilter`, `ApplyHighPassFilter`, `ApplyBitcrush`), `SoundSystem`, and WAV exporter.
- `scripts/ym2612_bank.go`: SEGA Mega Drive YM2612 4-operator FM + PolyBLEP SN76489 PSG + drum synth.
- `scripts/gm_instruments.go`: General MIDI program (`0..127`) and Channel 10 drum resolver (`27..87`).
- `scripts/apple_synth_darwin.go` & `scripts/apple_synth_other.go`: Native macOS `AudioToolbox` `-apple` renderer backed by `gs_instruments.dls`.
- `scripts/play.go`: CLI runner (`validate`, `play`, `demo`, `export`, `synth-json`, `presets-json`).
- `scripts/sound_test.go`: Unit tests for drift-free rational timing, `ValidateScoreTheory`, mute behavior, and all bundled scores.
- **9 reference scores in `scripts/`**:
  - Classic 16-bit study tracks: `bare_knuckle_intro.music`, `ground_zero.music`, `gaiares_level2.music`, `shinobi2_stage2.music`, `elemental_master_stage1.music`.
  - Original game tracks: `dawn_strategy_battle.music`, `despair_theme.music`, `battle_theme.music`, `credits_theme.music`.

---

## Core architecture and DSP helpers

- **Dual synthesis and soft-knee limiter**: Cumulative rational-time rounding (`int(math.Round(cursorSec * 44100))`) eliminates beat drift across `:16`, `:8t`, and `:4t` tuplets. A $C^1$-continuous soft limiter compresses multi-track peaks above `85%` full scale without hard clipping.
- **Per-track stem isolation (`1:1` channel rule)**: Give each declared `inst` one dedicated `track` so `SynthesizeScoreWithStems` exports matching per-channel stems alongside the master mix (`vol=0` mutes both melodic and drum channels).
- **Mandatory 4-byte PCM alignment (`&^ 3`)**: Each `44.1 kHz` 16-bit little-endian stereo frame is `4` bytes (`176,400` bytes/sec). Mask buffer lengths and `Seek()` offsets with `&^ 3` (`aligned := len(pcm) &^ 3`) to prevent Ebitengine panics.
- **Runtime DSP utilities**: `SliceLoopPCM(pcm, startSec, endSec)`, `ApplyLowPassFilter(pcm, alpha)`, `ApplyHighPassFilter(pcm, alpha)`, and `ApplyBitcrush(pcm, bits, downsample)`.

---

## Quick-start `.music` DSL and CLI workflow

See [`references/dsl_spec.md`](references/dsl_spec.md) for all waveforms, Italian tempo markings, `~` / `~ |` ties, `(...):dur` groups, and `@` dynamics.

```text
title "Stage 1 - Ruined Spire"
type song
tempo allegro 132
time 4/4

inst lead  wave=ym2612_brass      pan=-0.15
inst bass  wave=ym2612_slap_bass  pan=0.00
inst drums wave=kick              vol=0.28 pan=0.00

pattern p_lead  = E5:2 C5:4 G4:4 | A4:2. G4:4 |
pattern p_bass  = (C2 C2 C3 C2):8*2 | (A1 A1 A2 A1):8*2 |
pattern p_drums = kick:8 hat:8 snare:8 hat:8 kick:8 hat:8 snare:8 (tom_hi*2):16 |

track ch01 lead:  p_lead*2
track ch02 bass:  p_bass*2
track ch03 drums: p_drums*2
```

Run CLI commands from the skill root (`go run ./scripts <command> ...`):

```bash
# Run full Go unit tests
(cd scripts && go test -v ./...)

# Validate music theory, consonance, barlines, >= 8 channels, and >= 30s duration
go run ./scripts validate scripts/bare_knuckle_intro.music

# Validate short fanfares or stingers with custom thresholds
go run ./scripts validate -min-channels 6 -min-duration 6 victory_fanfare.music

# Emit single-line JSON diagnostics, optional WAV, and packed per-track stems
go run ./scripts synth-json -out stage.wav -stems stage.stems scripts/bare_knuckle_intro.music
go run ./scripts synth-json -apple -solo ch01,ch02 scripts/bare_knuckle_intro.music

# Inspect waveforms/presets/scores catalog, export WAV, or audition playback
go run ./scripts presets-json
go run ./scripts export scripts/bare_knuckle_intro.music stage.wav
go run ./scripts export -apple scripts/bare_knuckle_intro.music stage_apple.wav
go run ./scripts play -loop scripts/bare_knuckle_intro.music

# Fast iteration: build CLI binary once to skip recompiling per run
go build -o /tmp/music_cli ./scripts && /tmp/music_cli validate scripts/*.music
```

---

## Quality checklist for original compositions

Review full voice-leading rules in [`references/music_theory_and_arranging.md`](references/music_theory_and_arranging.md) before finalizing any `.music` score:

1. **Pick a distinct tempo, mode, and palette first** (`70` to `175 BPM`) matched to the scene rather than reusing a template.
2. **Layer `8` to `12+` tracks over `30s` to `150s+`** with a clear macro-form (intro, verse, chorus/climax, bridge/turnaround, fade).
3. **Preserve phrasing continuity**: Tie held notes across barlines (`~` or `~ |`), articulate repeated chord stabs with `R:16`, and verify every bar with `|` barlines.
4. **Anchor `C1` to `C2` bass** so `50%` to `75%` of spectral energy lives under `260 Hz` without stationary noise on drums or leads.
5. **Pass `ValidateProductionBGM`** (`go run ./scripts validate`) with clean diatonic/modal voice-leading (no sustained minor seconds, flat ninths, or simultaneous `G` vs. `G#`).
6. **Pre-compile at startup** with `&^ 3` aligned lengths and seek offsets.

---

## Zero-allocation Ebitengine integration

MP3 encoders insert priming/padding silence (`~1,152` samples) that creates audible pops at loop boundaries. Pre-compiling `.music` text scores (`5 KB` to `20 KB`) to raw `44.1 kHz` PCM at boot produces sample-exact loops with zero Cgo dependencies on desktop and WebAssembly.

1. Copy the pure-Go synth files (`sound.go`, `ym2612_bank.go`, `gm_instruments.go`, plus optional `apple_synth_*.go`) into `internal/audio/procmusic/`.
2. Embed `.music` scores via `//go:embed` and compile once during game or scene initialization:

```go
//go:embed assets/music/dawn_strategy_battle.music
var battleBGMDSL string

type AudioBank struct {
	audioCtx     *audio.Context
	soundSys     *procmusic.SoundSystem
	battlePlayer *audio.Player
}

func NewAudioBank() (*AudioBank, error) {
	audioCtx := audio.NewContext(44100)
	battlePCM, err := procmusic.CompileDSL(battleBGMDSL)
	if err != nil {
		return nil, err
	}
	// Enforce mandatory 4-byte frame alignment (&^ 3)
	alignedLen := int64(len(battlePCM)) &^ 3
	loopStream := audio.NewInfiniteLoop(bytes.NewReader(battlePCM[:alignedLen]), alignedLen)
	battlePlayer, err := audioCtx.NewPlayer(loopStream)
	if err != nil {
		return nil, err
	}
	return &AudioBank{
		audioCtx:     audioCtx,
		soundSys:     procmusic.NewSoundSystem(audioCtx),
		battlePlayer: battlePlayer,
	}, nil
}
```

- Pause and rewind (`player.Pause()`, `player.Rewind()`) or step `player.SetVolume()` smoothly across transitions, and share the same `audio.Context` with `procedural-sfx` (`PlaySFX` cooldowns `30ms` to `60ms`) so rapid cues never clip channels.
