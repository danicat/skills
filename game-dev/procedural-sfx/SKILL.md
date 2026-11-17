---
name: procedural-sfx
description: >
  Pure-code procedural game sound effect (SFX) synthesis engine and .sfx DSL
  for Ebitengine. Compiles 4-byte aligned 16-bit 44.1 kHz stereo PCM cues in
  memory with PolyBLEP anti-aliasing, 18 archetype presets, duty and SVF filter
  sweeps, Galois LFSR chiptune noise, 2-operator FM, soft-clipping, boundary
  micro-fades, and acoustic QA validation.
license: Apache-2.0
metadata:
  category: game-dev
  tags: "sfx, audio, dsp, synthesis, chiptune, ebitengine"
  author: Daniela Petruzalek (daniela@danicat.dev)
  version: "0.4.0"
  catalog: https://skills.danicat.dev
---

# Procedural sound effects: SFX DSL and synthesis engine

`procedural-sfx` compiles plain-text `.sfx` scripts directly into `44.1 kHz`, 16-bit signed little-endian stereo PCM buffers (`[]byte`) in memory with zero external audio files.

- **Complete `.sfx` DSL grammar and 18-preset reference**: [`references/sfx_dsl.md`](references/sfx_dsl.md)

---

## Companion skills

- **`procedural-music`**: Companion skill for multi-track background music (`.music`). Both synthesize 4-byte aligned `44.1 kHz` stereo PCM, while keeping SFX (`18` presets, SVF sweeps, LFSR noise, pitch curves) separate from multi-bar musical scores.
- **`lyria`**: Pair `procedural-sfx` for fast, predictable gameplay cues (lasers, hits, jumps, UI ticks) with `lyria` when a game calls for AI-generated ambient stems or soundtracks.
- **`game-design` and `vibe-game-developer`**: Map each player verb, hitstop, screen shake, and UI state transition to a distinct sound silhouette so actions feel physical without cluttering the mix.
- **`ebitengineer`**: Pre-compile `.sfx` scripts once at boot, mask buffer lengths and seek offsets with `&^ 3`, share a single `audio.Context`, and enforce per-cue cooldowns inside `Update()`.

---

## Available scripts and curated SFX library

Run CLI commands from the skill root (`go run ./scripts <command> ...`) or run tests inside `scripts/`:

- `scripts/sound.go`: DSL parser (`ParseDSL`, `CompileDSL`, `LoadDSLFile`), preset catalog (`GetSFXPreset`, `ListSFXPresets`), synth engine (`SynthesizeScore`), acoustic validator (`ValidateProductionSFX`, `ValidateScore`), and WAV exporter (`ExportWAV`).
- `scripts/play.go`: CLI runner (`play`, `demo`, `validate`, `presets`, `presets-json`, `export`, `synth-json`).
- `scripts/sound_test.go`: Unit tests for DSP primitives, PolyBLEP, soft-clipping, LFSR noise, track muting, and all `18` curated cues.
- **18 curated `.sfx` cues in `scripts/`**:
  - Weapons and impacts: `laser_arcade.sfx`, `plasma_gun.sfx`, `explosion_arcade.sfx`, `explosion_deep.sfx`, `sword_clash.sfx`, `shield_deflect.sfx`, `hit_punch.sfx`, `hit_damage.sfx`.
  - Movement and pickups: `jump_arcade.sfx`, `jump_spring.sfx`, `coin_pickup.sfx`, `gem_shimmer.sfx`, `powerup_fanfare.sfx`, `footstep_stone.sfx`, `engine_thruster.sfx`.
  - UI cues: `ui_select.sfx`, `ui_confirm.sfx`, `ui_error.sfx`.

```bash
# Run automated unit tests and curated cue checks
(cd scripts && go test -v ./...)

# Validate .sfx files against production thresholds
go run ./scripts validate scripts/*.sfx

# Play an .sfx file (add -loop for continuous cues) or play the showcase demo
go run ./scripts play scripts/laser_arcade.sfx
go run ./scripts play -loop scripts/engine_thruster.sfx
go run ./scripts demo

# List all 18 archetype presets (table or JSON) and inspect a single cue as JSON
go run ./scripts presets
go run ./scripts presets-json
go run ./scripts synth-json -out laser.wav scripts/laser_arcade.sfx

# Export a compiled .sfx cue to a 44.1 kHz 16-bit stereo WAV file
go run ./scripts export scripts/laser_arcade.sfx laser.wav
```

---

## Core DSP architecture

1. **PolyBLEP anti-aliasing**: Applies polynomial band-limited step correction around phase wraps and pulse-width transitions on `square` and `sawtooth` waves so high pitches avoid aliasing buzz above Nyquist (`22,050 Hz`).
2. **16-bit Galois LFSR noise (`wave=psg_noise`)**: Uses maximal-period taps (`x^16 + x^14 + x^13 + x^11 + 1`) clocked from target pitch for classic console explosions and metallic textures.
3. **Dynamic Chamberlin SVF filters (`lpf`, `hpf`, `q`)**: Interpolates cutoff frequency per sample (`lpf=3500->400 q=2.2`) for organic energy blasts and filtered booms.
4. **Pulse-width sweeps (`duty=start->end`)**: Sweeps duty cycle (`0.50 -> 0.125`) across a note for animated lasers and synth tones.
5. **Pitch trajectories (`curve=exp|lin|hyper`)**: `exp` sweeps musical intervals cleanly for lasers and jumps; `lin` drives crisp UI ticks; `hyper` snaps rapidly from transient to bass body for punches.
6. **Dynamic 2-operator FM (`fm`, `mod_ratio`, `mod_freq`, `mod_index`)**: Produces coins, crystals, and inharmonic sword clangs (`mod_ratio=2.76` or `mod_freq=620Hz`).
7. **$C^1$ smooth soft-clipping (`SoftClip`)**: Passes amplitude up to `0.75` linearly and compresses peaks toward `1.0` (`0 dBFS`) so multi-track stacks never wrap or clip harsh edges.
8. **Anti-click boundary fades**: Applies a `44`-frame (`~1ms`) raised-cosine fade-in from zero and fade-out to zero on every cue.

---

## Quick-start `.sfx` DSL syntax

Layer synchronized `track` stems starting at `t = 0`, chain inline `seq` events, or trigger single-line `step` cues. See [`references/sfx_dsl.md`](references/sfx_dsl.md) for all attributes and the 18 built-in `preset=` table.

```text
title "Deep Cinematic Explosion"
type sfx

inst transient wave=noise noise_filter=0.90 vol=0.32 adsr=0.001,0.04,0.00,0.04 hpf=800
inst rumble    preset=explosion_deep vol=0.40 adsr=0.005,0.25,0.25,0.55

track punch transient: transient:80ms R:720ms
track boom  rumble:    120Hz->20Hz:800ms
```

- Single-channel sequences: `seq: laser(950Hz->120Hz):150ms R:100ms | coin(B5):70ms coin(E6):220ms`
- One-line cues: `step preset=arcade_laser dur=140ms`
- Built-in presets (`preset=`): `arcade_laser`, `plasma_gun`, `explosion_arcade`, `explosion_deep`, `coin_pickup`, `gem_shimmer`, `jump_arcade`, `jump_spring`, `sword_clash`, `shield_deflect`, `hit_punch`, `hit_damage`, `powerup_fanfare`, `ui_select`, `ui_confirm`, `ui_error`, `footstep_stone`, `engine_thruster`.

---

## Acoustic envelope and multi-layer sound design

Convincing impacts model three distinct physical stages:

```text
Amplitude
  1.0 |    /\   <-- 1. Transient (1 to 15 ms: sharp high-frequency snap)
      |   /  \
  0.5 |  /    \______  <-- 2. Body (15 to 150 ms: pitch sweep & fundamental weight)
      | /            \________
  0.0 +-----------------------\--> Time (ms)
                               \-- 3. Tail (150 to 600 ms: filtered decay & ring)
```

1. **Transient (`1ms` to `15ms`)**: Initial crack or spark using fast attack (`0.001` to `0.004` sec) and high-passed noise (`hpf=800` to `2200`) or bright FM modulation so cues cut through background music.
2. **Body (`15ms` to `150ms`)**: Core pitch drop carrying mass (`curve=hyper` for impacts, `curve=exp` for lasers and jumps).
3. **Tail (`150ms` to `600ms`)**: Room decay (`lpf=1200->150`, `mod_index=5.5->0.2`) settling cleanly to silence.

---

## Production validation (`ValidateProductionSFX`)

Every `.sfx` cue should pass `ValidateScore` and `ValidateProductionSFX` (`go run ./scripts validate scripts/*.sfx`):

- **Duration**: `10ms` (`0.01s`) to `5.0s`.
- **Non-silent energy**: Peak above `-60 dBFS` and RMS above `-70 dBFS`.
- **True peak headroom**: At or below `-0.1 dBFS` (`0.988` linear).
- **DC offset**: Mean bias within `+/-0.05` (`5%`) per channel.
- **Click-free edges**: First and last stereo frames within `+/-300` (`16-bit PCM`).

```text
STATUS  | CUE / FILE               | DURATION | PEAK L/R (dBFS) | RMS (dBFS) | DC OFFSET  | BOUNDARY
-----------------------------------------------------------------------------------------------
PASS    | coin_pickup.sfx          | 0.32s   | -16.8 / -16.8   | -24.9     | -0.0000    | Clean
PASS    | explosion_deep.sfx       | 0.80s   | -11.4 / -11.4   | -23.2     | +0.0006    | Clean
PASS    | sword_clash.sfx          | 0.25s   | -6.9 / -6.9     | -26.1     | -0.0004    | Clean
PASS    | ui_select.sfx            | 0.05s   | -16.4 / -16.4   | -29.5     | -0.0001    | Clean
```

---

## Zero-allocation Ebitengine integration

Pre-compile `.sfx` scripts into **4-byte aligned** `[]byte` buffers (`len(pcm) &^ 3`) at startup so `Update()` and `Draw()` never allocate or synthesize mid-frame. Enforce a per-cue cooldown (`30ms` to `60ms`) and fail fast on unknown cue names:

```go
type SoundManager struct {
	audioCtx *audio.Context
	sounds   map[string][]byte
	lastPlay map[string]time.Time
}

func AlignPCM(pcm []byte) []byte {
	return pcm[:len(pcm)&^3]
}

func NewSoundManager(audioCtx *audio.Context) (*SoundManager, error) {
	if audioCtx == nil {
		return nil, fmt.Errorf("sfx: nil audio.Context")
	}
	const laserDSL = `
title "Arcade Pulse Laser"
type sfx
inst laser preset=arcade_laser duty=0.50->0.125 vol=0.32
track main laser: 950Hz->110Hz:140ms
`
	laserPCM, err := CompileDSL(laserDSL)
	if err != nil {
		return nil, fmt.Errorf("compile laser SFX: %w", err)
	}
	if rep, err := ValidateProductionSFX(laserPCM); err != nil || !rep.Passed {
		return nil, fmt.Errorf("validate laser SFX: %w", err)
	}
	return &SoundManager{
		audioCtx: audioCtx,
		sounds:   map[string][]byte{"laser": AlignPCM(laserPCM)},
		lastPlay: make(map[string]time.Time, 8),
	}, nil
}

func (sm *SoundManager) PlaySFX(name string, cooldown time.Duration) error {
	pcm, ok := sm.sounds[name]
	if !ok {
		return fmt.Errorf("sfx: unknown cue %q", name)
	}
	if len(pcm) < 4 {
		return fmt.Errorf("sfx: cue %q has empty aligned buffer", name)
	}
	now := time.Now()
	if last, exists := sm.lastPlay[name]; exists && now.Sub(last) < cooldown {
		return nil
	}
	sm.lastPlay[name] = now
	player := sm.audioCtx.NewPlayerFromBytes(pcm[:len(pcm)&^3])
	player.Play()
	return nil
}
```
