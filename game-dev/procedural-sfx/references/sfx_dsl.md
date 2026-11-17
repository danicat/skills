# Procedural SFX DSL and Preset Reference

Complete grammar for `.sfx` sound effect scripts, instrument parameters, event syntax, track layering, and the 18 built-in archetype presets compiled by [`../scripts/sound.go`](../scripts/sound.go).

---

## 1. Header directives

```text
title "Heavy Grenade Explosion"
type sfx
bpm 120
time 4/4
filter lpf 0.35
bitcrush 8 2
loop 50ms 950ms
```

- Comments start with `#` (at line start or after whitespace) or `//`.
- `title "<name>"`: Human-readable cue name used in logs and validation reports.
- `type sfx`: Marks the script as a sound effect cue.
- `bpm <1..1000>`: Reference tempo when using musical beat durations (`:4`, `:8`, `:16`). Defaults to `120`.
- `time <num>/<den>`: Optional time signature (defaults to `4/4`).
- `filter <lpf|hpf> <alpha>`: Optional master bus single-pole filter using a smoothing coefficient `alpha` in `(0.0, 1.0]`.
- `bitcrush <bits> <downsample>`: Optional master bus lo-fi decimation (`bits` from `1` to `16`, `downsample >= 1`).
- `loop <startDur> <endDur>`: Optional loop slice window using durations such as `50ms 950ms` or `0.05s 0.95s`.

---

## 2. Instrument definitions (`inst`)

Each instrument declares `preset=<name>` or `wave=<type>`, followed by optional parameter overrides:

```text
inst <name> [preset=<preset_name>] [wave=<type>] [vol=<0..1>] [pan=<-1..1>]
            [duty=<val|start->end>] [adsr=<A>,<D>,<S>,<R>]
            [freq=<pitchOrSweep>] [curve=<exp|lin|hyper>]
            [lpf=<Hz|start->end>] [hpf=<Hz|start->end>] [q=<0.1..20>]
            [fm=<ratioOrHz>,<index|start->end>] [mod_ratio=<val>] [mod_freq=<Hz>] [mod_index=<val|start->end>]
            [noise=<filterCoeff>,<blend>] [noise_filter=<(0..1]>] [noise_blend=<0..1>]
            [vib=<rateHz>,<depthHz>] [bitcrush=<bits>,<downsample>]
```

### Waveforms (`wave=`)
- `square` (or `pulse`, `sq`): PolyBLEP band-limited pulse wave with variable duty cycle.
- `sawtooth` (or `saw`): PolyBLEP band-limited sawtooth wave.
- `triangle` (or `tri`): Warm low-harmonic triangle wave for jumps, kicks, and punches.
- `sine` (or `sin`): Pure fundamental tone for sub-bass drops and clean UI ticks.
- `noise` (or `white_noise`): Filtered white noise for impacts, wind, and footsteps.
- `psg_noise` (or `periodic_noise`, `psg`): 16-bit Galois LFSR chiptune noise.
- `fm`: 2-operator frequency modulation synthesizer.

### Attribute reference
- `preset=<name>` (or `template=`, `archetype=`): Copies baseline parameters from one of the 18 built-in presets before applying subsequent overrides.
- `vol=<0.0..1.0>`: Voice gain multiplier (default `0.20`, or `0.0` to mute). Keep stacked tracks around `0.18` to `0.42` to stay inside the linear headroom zone.
- `pan=<-1.0..1.0>`: Constant-power stereo panning (`-1.0` full left, `0.0` center, `+1.0` full right).
- `duty=<val>` or `duty=<start->end>`: Pulse width in `(0.0, 1.0)` (for example, `duty=0.50->0.125`).
- `adsr=<A>,<D>,<S>,<R>`: Envelope Attack, Decay, Sustain (`0..1`), and Release. Attack, Decay, and Release accept seconds (`0.04`) or duration suffixes (`40ms`). Individual fields (`attack=`, `decay=`, `sustain=`, `release=`) are also supported.
- `freq=<pitchOrSweep>` (or `sweep=`, `pitch=`): Default pitch or sweep when triggered without an explicit note (`freq=950Hz->110Hz`).
- `curve=<exp|lin|hyper>`: Pitch sweep curve (`exp` default).
- `lpf=<val|start->end>` and `hpf=<val|start->end>`: Per-voice SVF filter cutoff in Hz (`lpf=3500->400` or `hpf=800Hz`) or alpha coefficient (`<= 1.0`).
- `q=<0.1..20.0>` (or `res=`, `resonance=`): SVF filter resonance factor (`0.707` Butterworth default).
- `fm=<ratioOrHz>,<index|start->end>`: Shorthand for modulator ratio/frequency and modulation index (`fm=2.76,2.2->0.2` or `fm=620Hz,5.5->0.5`). Individual attributes (`mod_ratio=`, `mod_freq=`, `mod_index=`) are also supported.
- `noise=<filterCoeff>,<blend>`: Sets both single-pole noise LPF coefficient in `(0.0, 1.0]` and oscillator-to-noise blend in `[0.0, 1.0]`. Individual attributes (`noise_filter=`, `noise_blend=`) are also supported.
- `vib=<rateHz>,<depthHz>`: Pitch vibrato LFO speed and depth in Hz (`vib=18,25`).
- `bitcrush=<bits>,<downsample>`: Per-instrument bitcrusher (`bitcrush=6,4`).

---

## 3. Events, tracks (`track`), sequences (`seq`), and steps (`step`)

Track events pair a pitch, sweep, chord, instrument trigger, or rest with a `:duration` suffix:
- **Frequency sweep**: `950Hz->110Hz:140ms` or pitch glide `C5->C2:180ms`.
- **Fixed pitch**: `440Hz:80ms`, `B5:75ms`, or `E6:240ms`.
- **Inline instrument trigger**: `laser(950Hz->110Hz):140ms` or `coin(B5):70ms`.
- **Preset default trigger**: `roar:450ms` or `:450ms` (uses the instrument's default start/end frequencies).
- **Chord**: `[C5 E5 G5]:200ms` or `horn[C5 E5 G5]:200ms`.
- **Rest**: `R:150ms` (or `r`, `_`, `.`).
- **Grouping, repeats, and transposition**: `(B5:60ms E6:120ms)*2` or `pattern_name@+12`.

Durations accept milliseconds (`80ms`), seconds (`0.4s`), beats (`2b`), or musical subdivisions (`:4`, `:8`, `:16`, `:16.`, `:8t`). Omitting `:duration` inherits the previous token's duration on that track.

- **`track <name> <default_inst>:`**: Layer synchronized channels starting at `t = 0`:
  ```text
  title "Deep Cinematic Explosion"
  type sfx

  inst transient wave=noise noise_filter=0.90 vol=0.32 adsr=0.001,0.04,0.00,0.04 hpf=800
  inst rumble    preset=explosion_deep vol=0.40 adsr=0.005,0.25,0.25,0.55

  track punch transient: transient:80ms R:720ms
  track boom  rumble:    120Hz->20Hz:800ms
  ```
- **`seq:` or `seq <default_inst>:`**: Single-channel sequence switching instruments inline:
  ```text
  seq:
    laser(950Hz->120Hz):150ms R:100ms |
    coin(B5):70ms coin(E6):220ms
  ```
- **`step`**: One-line cue without a separate `inst` declaration:
  ```text
  step preset=arcade_laser dur=140ms
  ```

---

## 4. Built-in 18 SFX archetype presets (`preset=<name>`)

Inspect full preset fields at any time via `go run ./scripts presets`:

| Preset Name | Wave | Default Sweep | Filter / Modulation | Curve | Typical Game Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `arcade_laser` | `square` | `950->110 Hz` | `duty=0.50->0.15` | `exp` | Retro sci-fi blasters, laser cannons |
| `plasma_gun` | `sawtooth` | `1200->180 Hz` | `lpf=3500->400`, `q=2.2` | `exp` | Heavy sci-fi energy weapons |
| `explosion_arcade` | `psg_noise` | `180->25 Hz` | `lpf=1200->150`, `q=1.8` | `exp` | Classic 8-bit and 16-bit explosions |
| `explosion_deep` | `sine` | `120->24 Hz` | `noise=0.15,0.45` | `exp` | Heavy bomb detonations, boss slams |
| `coin_pickup` | `square` | `988->1319 Hz` | `duty=0.50`, snappy ADSR | `exp` | Coins, score pickups, collectibles |
| `gem_shimmer` | `fm` | `1568->1568 Hz` | `mod_ratio=2.76`, `mod_index=2.2->0.2` | `exp` | Rare crystals, magic chimes, loot |
| `jump_arcade` | `square` | `160->620 Hz` | `duty=0.50`, upward sweep | `exp` | Platformer character jumps |
| `jump_spring` | `triangle` | `120->480 Hz` | `vib=18,25` | `exp` | Bouncy springs, bumpers, trampolines |
| `sword_clash` | `fm` | `520->210 Hz` | `mod_freq=620Hz`, `mod_index=5.5->0.5`, `noise=0.60,0.25` | `exp` | Blade parries, weapon collisions |
| `shield_deflect` | `fm` | `880->440 Hz` | `mod_ratio=3.1415`, `mod_index=4.0->0.2` | `exp` | Energy shields, armor ricochets |
| `hit_punch` | `triangle` | `180->45 Hz` | `noise=0.45,0.30` | `hyper` | Melee punches, body impacts |
| `hit_damage` | `sawtooth` | `220->65 Hz` | `noise=0.30,0.38` | `exp` | Player hurt or enemy hit crunch |
| `powerup_fanfare` | `square` | `523->1047 Hz` | `duty=0.35`, bright sustain | `exp` | Level-up arpeggios, stage clear |
| `ui_select` | `sine` | `880->1100 Hz` | Ultra-short `1ms` attack | `lin` | Menu cursor hover and navigation |
| `ui_confirm` | `square` | `659->1319 Hz` | `duty=0.50`, bright chime | `exp` | Button press, dialog confirmation |
| `ui_error` | `sawtooth` | `150->110 Hz` | Downward buzz | `lin` | Locked door, invalid action, cancel |
| `footstep_stone` | `noise` | Filtered noise | `noise_filter=0.25`, short decay | `exp` | Walking or landing on hard surfaces |
| `engine_thruster` | `psg_noise` | `110->110 Hz` | `noise_filter=0.35`, `sustain=0.80` | `exp` | Ship thrusters, machinery rumble |
